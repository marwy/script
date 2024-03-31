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
  .top_menu_div {
    animation: blink 1s linear infinite;
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
const menuDivIn = document.querySelector('.top_menu_div .top_menu_div_in');

// Загрузите изображение логотипа.
const logoSrc = 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Twitter_Verified_Badge.svg/2048px-Twitter_Verified_Badge.svg.png';

// Создайте новый элемент img для логотипа.
const logoImg = document.createElement('img');
logoImg.src = logoSrc;
logoImg.style.height = '20px'; // Вы можете изменить это значение, чтобы подогнать размер логотипа.
logoImg.style.display = 'inline-block'; // Задайте свойство display для изображения.
logoImg.style.marginLeft = '10px'; // Добавьте немного пространства между текстом и лого.

// Добавьте логотип в menuDivIn.
menuDivIn.appendChild(logoImg);
