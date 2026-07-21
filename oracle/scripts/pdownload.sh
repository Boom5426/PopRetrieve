#!/bin/bash
# Parallel chunked downloader (NCBI throttles per-connection; ranges bypass it).
# Usage: pdownload.sh URL OUT [N_CONN]
set -u
URL="$1"; OUT="$2"; N="${3:-16}"
SIZE=$(curl -sIL "$URL" | grep -i '^content-length' | tail -1 | tr -dc '0-9')
[ -z "$SIZE" ] && { echo "no size"; exit 1; }
CHUNK=$(( (SIZE + N - 1) / N ))
PD="$OUT.parts"; mkdir -p "$PD"
echo "size=$SIZE N=$N chunk=$CHUNK"
for pass in 1 2 3 4 5; do
  ok=1; pids=()
  for i in $(seq 0 $((N-1))); do
    START=$((i*CHUNK)); END=$((START+CHUNK-1)); [ $END -ge $SIZE ] && END=$((SIZE-1))
    WANT=$((END-START+1)); P="$PD/part_$i"
    HAVE=$(stat -c%s "$P" 2>/dev/null || echo 0)
    [ "$HAVE" -eq "$WANT" ] && continue
    ok=0
    curl -s -r ${START}-${END} "$URL" -o "$P" & pids+=($!)
  done
  [ $ok -eq 1 ] && { echo "all parts complete (pass $pass)"; break; }
  echo "pass $pass: downloading $((${#pids[@]})) parts..."; wait
done
cat "$PD"/part_* > "$OUT"
GOT=$(stat -c%s "$OUT")
echo "assembled size=$GOT expected=$SIZE"
[ "$GOT" -eq "$SIZE" ] && { rm -rf "$PD"; echo "OK"; } || { echo "SIZE MISMATCH - parts kept"; exit 1; }
