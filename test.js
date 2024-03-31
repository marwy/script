// Импортируйте необходимые библиотеки
import * as THREE from 'https://threejs.org/build/three.module.js';
import { OrbitControls } from 'https://threejs.org/examples/jsm/controls/OrbitControls.js';
import { CannonPhysics } from './CannonPhysics.js'; // CannonPhysics - это обертка над cannon.js. Вам необходимо будет создать этот файл.

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
const controls = new OrbitControls(camera, renderer.domElement);

// Инициализируйте физику
const physics = new CannonPhysics();

// Создайте mesh
const geometry = new THREE.BoxGeometry();
const material = new THREE.MeshNormalMaterial();
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

// Создайте тело и добавьте его в world
const cubeBody = physics.createBox(geometry.parameters.width, geometry.parameters.height, geometry.parameters.depth);
cubeBody.position.y = 5; // Установите начальную позицию немного выше верхушки
physics.world.addBody(cubeBody);

camera.position.z = 5;

// Обновите позицию и вращение mesh в соответствии с физическим телом
const animate = function () {
    requestAnimationFrame(animate);
    cube.position.copy(cubeBody.position);
    cube.quaternion.copy(cubeBody.quaternion);
    renderer.render(scene, camera);
};

animate();
