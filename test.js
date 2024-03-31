const menuDiv = document.querySelector('.top_menu_div');

// Создайте стиль, который будет добавлен в документ
const style = document.createElement('style');
style.textContent =
  `
  @keyframes blink {
    0% {color: lightgreen; background-color: #2D4AC5;}
    50% {color: black; background-color: #3096F8;}
    100% {color: lightgreen; background-color: #2D4AC5;}
  }
  .top_menu_div {
    animation: blink 1s linear infinite;
    background-image: linear-gradient(to right, #3096F8, #2D4AC5);
    border-radius: 8px;
    padding: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    color: #fff;
  }
  `;

// Добавьте созданный стиль в документ
document.head.appendChild(style);
