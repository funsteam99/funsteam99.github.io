(() => {
  const rails = document.querySelectorAll('.comic-guide__rail');

  rails.forEach((rail) => {
    let pointerId = null;
    let startX = 0;
    let startScrollLeft = 0;
    let dragged = false;

    rail.addEventListener('pointerdown', (event) => {
      if (event.pointerType !== 'mouse' || event.button !== 0) return;

      pointerId = event.pointerId;
      startX = event.clientX;
      startScrollLeft = rail.scrollLeft;
      dragged = false;
      rail.classList.add('is-dragging');
      rail.setPointerCapture(pointerId);
      event.preventDefault();
    });

    rail.addEventListener('pointermove', (event) => {
      if (event.pointerId !== pointerId) return;

      const distance = event.clientX - startX;
      if (Math.abs(distance) > 6) dragged = true;
      rail.scrollLeft = startScrollLeft - distance;
      event.preventDefault();
    });

    const finishDrag = (event) => {
      if (event.pointerId !== pointerId) return;
      if (rail.hasPointerCapture(pointerId)) rail.releasePointerCapture(pointerId);
      pointerId = null;
      rail.classList.remove('is-dragging');
    };

    rail.addEventListener('pointerup', finishDrag);
    rail.addEventListener('pointercancel', finishDrag);
    rail.addEventListener('lostpointercapture', () => {
      pointerId = null;
      rail.classList.remove('is-dragging');
    });

    rail.addEventListener('click', (event) => {
      if (!dragged) return;
      event.preventDefault();
      event.stopPropagation();
      dragged = false;
    }, true);

    rail.addEventListener('dragstart', (event) => event.preventDefault());
  });
})();
