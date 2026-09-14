const panels = {
  direction: {
    number: '01 / Direction',
    title: 'Does a candidate align with the target response direction?',
    copy: 'Direction-only cosine similarity compares mean response orientation while deliberately discarding response magnitude and cell-to-cell structure.',
    note: 'Direction is a useful starting point, but it cannot distinguish an advantage caused by response magnitude from one caused by population structure.'
  },
  magnitude: {
    number: '02 / Magnitude',
    title: 'Does response magnitude explain the apparent retrieval gain?',
    copy: 'Mean L2 distance preserves both the direction and scale of the mean response, making it the necessary control for a population-level score.',
    note: 'A gain over direction-only cosine does not by itself show that full response-population structure was needed.'
  },
  population: {
    number: '03 / Population structure',
    title: 'Does the full response population change the candidate order?',
    copy: 'Energy distance, MMD, sliced Wasserstein, and subpopulation coverage compare cellular response distributions beyond a single response vector.',
    note: 'Population information is decision-relevant only when it changes candidate ordering beyond the magnitude-aware mean baseline.'
  },
  prediction: {
    number: '04 / Forward prediction',
    title: 'Does a population advantage survive predict-then-rank evaluation?',
    copy: 'A retrieval advantage measured from observed responses must be tested again after the response is predicted in the held-out setting.',
    note: 'Biological and functional evaluation can weaken an observed population-level advantage, so response matching is not the final decision criterion.'
  }
};

document.querySelectorAll('.diagnostic').forEach((button) => {
  button.addEventListener('click', () => {
    const panel = panels[button.dataset.panel];
    document.querySelectorAll('.diagnostic').forEach((item) => {
      const active = item === button;
      item.classList.toggle('active', active);
      item.setAttribute('aria-selected', String(active));
    });
    document.querySelector('#panel-number').textContent = panel.number;
    document.querySelector('#panel-title').textContent = panel.title;
    document.querySelector('#panel-copy').textContent = panel.copy;
    document.querySelector('#panel-note').textContent = panel.note;
  });
});

const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#site-nav');

menuButton?.addEventListener('click', () => {
  const open = navigation.classList.toggle('is-open');
  menuButton.setAttribute('aria-expanded', String(open));
});

navigation?.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
  navigation.classList.remove('is-open');
  menuButton?.setAttribute('aria-expanded', 'false');
}));

document.querySelectorAll('.copy-button').forEach((button) => button.addEventListener('click', async () => {
  const target = document.querySelector(`#${button.dataset.copyTarget}`);
  if (!target) return;
  try {
    await navigator.clipboard.writeText(target.innerText);
    button.textContent = 'Copied';
    setTimeout(() => { button.textContent = 'Copy'; }, 1600);
  } catch {
    button.textContent = 'Select code';
  }
}));
