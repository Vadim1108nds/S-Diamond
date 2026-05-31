import * as THREE from 'three';
import { OrbitControls } from 'https://unpkg.com/three@0.128.0/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'https://unpkg.com/three@0.128.0/examples/jsm/loaders/GLTFLoader.js';

let scene, camera, renderer, controls;
let currentModel = null;
let currentType = 'ring';

const CAMERA_SETTINGS = {
    ring: { pos: { x: 2, y: 1.5, z: 3.5 }, target: { x: 0, y: 0, z: 0 } },
    earrings: { pos: { x: 2, y: 1.8, z: 3.2 }, target: { x: 0, y: 0, z: 0 } },
    bracelet: { pos: { x: 2.2, y: 1.2, z: 3.8 }, target: { x: 0, y: 0.2, z: 0 } }
};

const OBJECTS = {
    ring: { metalPart: 'Ring', stonePart: 'Ring_gem' },
    earrings: { metalPart: 'Earring', stonePart: 'Earring_gem' },
    bracelet: { metalPart: 'braslet_material', stonePart: 'braslet_gem' }
};

const metalColors = { gold: 0xffcc44, silver: 0xe0e0e0, platinum: 0xeeeeee };
const stoneColors = { diamond: 0xffffff, sapphire: 0x3a6ea5, amethyst: 0xaa80ff };

let metalMesh = null;
let stoneMesh = null;

function init3D() {
    const container = document.getElementById('canvas-container');
    if (!container) return;
    const width = container.clientWidth, height = container.clientHeight;

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf5f0e8);

    camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(2, 1.5, 3.5);
    camera.lookAt(0, 0, 0);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.shadowMap.enabled = true;
    container.appendChild(renderer.domElement);

    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 1.2;
    controls.enableZoom = true;
    controls.zoomSpeed = 1.0;
    controls.target.set(0, 0, 0);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.65);
    scene.add(ambientLight);

    const mainLight = new THREE.DirectionalLight(0xfff5e8, 0.9);
    mainLight.position.set(2, 3, 2);
    mainLight.castShadow = true;
    scene.add(mainLight);

    const fillLight = new THREE.PointLight(0xccaa88, 0.5);
    fillLight.position.set(0, 1, 2);
    scene.add(fillLight);

    const backLight = new THREE.PointLight(0xffccaa, 0.4);
    backLight.position.set(-1, 1.5, -2);
    scene.add(backLight);

    const rimLight = new THREE.PointLight(0xffddbb, 0.45);
    rimLight.position.set(1, 1.8, -1.8);
    scene.add(rimLight);

    const bottomLight = new THREE.PointLight(0x88aaff, 0.3);
    bottomLight.position.set(0, -1.2, 0);
    scene.add(bottomLight);

    const fillFront = new THREE.PointLight(0xffeedd, 0.4);
    fillFront.position.set(0.5, 0.8, 2);
    scene.add(fillFront);

    animate();
}

function animate() {
    requestAnimationFrame(animate);
    if (controls) controls.update();
    if (renderer && scene && camera) renderer.render(scene, camera);
}

function updateCameraForType(type) {
    const cfg = CAMERA_SETTINGS[type] || CAMERA_SETTINGS.ring;
    camera.position.set(cfg.pos.x, cfg.pos.y, cfg.pos.z);
    controls.target.set(cfg.target.x, cfg.target.y, cfg.target.z);
    controls.update();
}

async function loadModel(type, url) {
    return new Promise((resolve) => {
        const loader = new GLTFLoader();
        loader.load(url, (gltf) => {
            const model = gltf.scene;
            if (currentModel) scene.remove(currentModel);
            currentModel = model;
            scene.add(model);

            metalMesh = null;
            stoneMesh = null;
            const cfg = OBJECTS[type];
            if (!cfg) return resolve(model);

            model.traverse((child) => {
                if (child.isMesh) {
                    if (child.name === cfg.metalPart) metalMesh = child;
                    if (cfg.stonePart && child.name === cfg.stonePart) stoneMesh = child;
                }
            });
            resolve(model);
        }, undefined, (error) => {
            console.error(error);
            createFallback(type);
            resolve(currentModel);
        });
    });
}

function createFallback(type) {
    if (currentModel) scene.remove(currentModel);
    if (type === 'ring') {
        const torus = new THREE.Mesh(new THREE.TorusGeometry(0.8, 0.2, 64, 128), new THREE.MeshStandardMaterial({ color: 0xffcc44, metalness: 0.9, roughness: 0.25 }));
        currentModel = torus;
        metalMesh = torus;
    } else if (type === 'earrings') {
        const group = new THREE.Group();
        const mat = new THREE.MeshStandardMaterial({ color: 0xffcc44, metalness: 0.8, roughness: 0.3 });
        const left = new THREE.Mesh(new THREE.SphereGeometry(0.4, 32, 32), mat);
        left.position.x = -0.6;
        const right = new THREE.Mesh(new THREE.SphereGeometry(0.4, 32, 32), mat);
        right.position.x = 0.6;
        group.add(left, right);
        currentModel = group;
        metalMesh = group;
    } else if (type === 'bracelet') {
        const knot = new THREE.Mesh(new THREE.TorusKnotGeometry(0.65, 0.12, 128, 16), new THREE.MeshStandardMaterial({ color: 0xffcc44, metalness: 0.85, roughness: 0.28 }));
        currentModel = knot;
        metalMesh = knot;
    }
    scene.add(currentModel);
}

function updateMetal(metal) {
    if (!metalMesh) return;
    const hex = metalColors[metal] || 0xffcc44;
    if (metalMesh.isGroup) {
        metalMesh.children.forEach(child => {
            if (child.material) child.material.color.setHex(hex);
        });
    } else if (metalMesh.material) {
        if (Array.isArray(metalMesh.material)) metalMesh.material.forEach(m => m.color.setHex(hex));
        else metalMesh.material.color.setHex(hex);
    }
}

function updateStone(stone) {
    if (!stoneMesh) return;
    if (stone === 'none') {
        stoneMesh.visible = false;
    } else {
        stoneMesh.visible = true;
        const hex = stoneColors[stone] || 0xffffff;
        if (stoneMesh.material) {
            if (Array.isArray(stoneMesh.material)) stoneMesh.material.forEach(m => m.color.setHex(hex));
            else stoneMesh.material.color.setHex(hex);
        }
    }
}

export async function setCustomization(type, metal, stone = 'none') {
    let url = '';
    if (type === 'ring') url = '/static/models/ring.glb';
    else if (type === 'earrings') url = '/static/models/earrings.glb';
    else if (type === 'bracelet') url = '/static/models/braslet.glb';
    if (url) await loadModel(type, url);
    else createFallback(type);
    updateCameraForType(type);
    updateMetal(metal);
    updateStone(stone);
}

window.addEventListener('load', () => {
    init3D();
    setCustomization('ring', 'gold', 'diamond');
});

export function capturePreview() {
    if (!renderer) return null;
    return renderer.domElement.toDataURL('image/png');
}