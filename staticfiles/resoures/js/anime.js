if (anime) {
  anime({
    targets: '.sidebar',
    translateX: [-300, 0],
    opacity: [0, 1],
    duration: 500,
    easing: 'easeOutBack'
  });

  anime({
    targets: '.card',
    translateY: [40, 0],
    opacity: [0, 1],
    delay: anime.stagger(100),
    easing: 'easeOutCubic',
    duration: 700
  });

  anime({
    targets: '.content-wrapper',
    opacity: [0, 1],
    translateY: [40, 0],
    duration: 800,
    easing: 'easeOutExpo'
  });

  anime({
      targets: '.card',
      translateY: [40, 0],
      opacity: [0, 1],
      delay: anime.stagger(100),
      easing: 'easeOutCubic',
      duration: 700
      });

  anime({
    targets: '.progress-bar-fill',
    width: '100%',
    easing: 'easeInOutQuad',
    duration: 1000
  });

  anime({
    targets: '.step-indicator.active',
    backgroundColor: '#4CAF50',
    scale: [0.8, 1],
    duration: 400,
    easing: 'easeOutBack'
  });

  anime({
    targets: '.form-field',
    translateY: [40, 0],
    opacity: [0, 1],
    delay: anime.stagger(100),
    duration: 600,
    easing: 'easeOutQuad'
  });

  // document.querySelectorAll("input").forEach((input) => {
  //   input.addEventListener("focus", () => {
  //     anime({
  //       targets: input,
  //       translateX: [
  //         { value: -5 }, 
  //         { value: 5 }, 
  //         { value: -3 },
  //         { value: 0 }
  //       ],
  //       duration: 300,
  //       easing: "easeInOutSine"
  //     });
  //   });
  // });
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
      anime({
        targets: link,
        scale: [1, 1.1, 1],
        duration: 300,
        easing: 'easeOutQuad'
      });
    });
  });

  // document.querySelectorAll('.btn').forEach(btn => {
//   btn.addEventListener('click', () => {
//     anime({
//       targets: btn,
//       scale: [1, 1.05, 1],
//       duration: 300,
//       easing: 'easeOutQuad'
//     });
//   });
// });
}