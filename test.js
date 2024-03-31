const menuDiv = document.querySelector('.top_menu_div');

// Создайте стиль, который будет добавлен в документ
const style = document.createElement('style');
style.textContent =
  `
  @keyframes blink {
    0% {color: lightgreen; background-color: #1a1a1a;}
    50% {color: #808080; background-color: #1a1a1a;}
    100% {color: lightgreen; background-color: #1a1a1a;}
  }

  @keyframes rotate {
    from {
      transform: rotateY(0deg);
    }
    to {
      transform: rotateY(1turn);
    }
  }

  .top_menu_div {

    perspective: 500px;
    transform-style: preserve-3d;

    animation: blink 1s linear infinite,
               rotate 5s infinite linear;

    background-image: none;
    background-color: #1a1a1a;
    border-radius: 8px;
    padding: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    color: #fff;
    text-shadow: 0 0 10px rgba(255,255,255,0.5), 0 0 20px rgba(255,255,255,0.5), 0 0 30px rgba(255,255,255,0.5), 0 0 40px #ff00de;
    font-size: 30px;
  }
  `;

// Добавьте созданный стиль в документ
document.head.appendChild(style);
