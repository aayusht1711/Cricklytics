import streamlit.components.v1 as components

def show_3d_background():
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    </head>
    <body>
        <script>
            try {
                const parentDoc = window.parent.document;
                
                // Remove existing container
                let existing = parentDoc.getElementById('three-bg-container');
                if (existing) existing.remove();

                // Create container                // --- 1. Glassmorphism Layering Fix ---
                const container = parentDoc.createElement('div');
                container.id = 'three-bg-container';
                container.style.position = 'fixed';
                container.style.top = '0';
                container.style.left = '0';
                container.style.width = '100vw';
                container.style.height = '100vh';
                container.style.zIndex = '0'; 
                container.style.pointerEvents = 'none'; 
                
                const appViewContainer = parentDoc.querySelector('[data-testid="stAppViewContainer"]') || parentDoc.body;
                appViewContainer.insertBefore(container, appViewContainer.firstChild);

                // Force Streamlit's main content to sit ABOVE the canvas
                const styleFix = parentDoc.createElement('style');
                styleFix.innerHTML = `
                    .main, [data-testid="stMainBlockContainer"], header, [data-testid="stSidebar"] {
                        position: relative !important;
                        z-index: 10 !important;
                    }
                `;
                parentDoc.head.appendChild(styleFix);

                // Setup Three.js Scene
                const scene = new THREE.Scene();
                // Add a subtle fog to blend into the dark dashboard background
                scene.fog = new THREE.FogExp2(0x080c10, 0.02);
                
                const camera = new THREE.PerspectiveCamera(45, window.parent.innerWidth / window.parent.innerHeight, 0.1, 1000);
                camera.position.z = 15;

                const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
                renderer.setSize(window.parent.innerWidth, window.parent.innerHeight);
                renderer.setPixelRatio(window.devicePixelRatio);
                renderer.toneMapping = THREE.ACESFilmicToneMapping;
                renderer.toneMappingExposure = 1.2;
                
                container.appendChild(renderer.domElement);

                // --- Cinematic Studio Lighting ---
                scene.add(new THREE.AmbientLight(0xffffff, 0.15));
                
                const keyLight = new THREE.DirectionalLight(0xfff5e6, 1.5);
                keyLight.position.set(5, 10, 8);
                scene.add(keyLight);
                
                const rimLight = new THREE.SpotLight(0x00e5ff, 2.5);
                rimLight.position.set(-10, -5, -5);
                rimLight.angle = Math.PI / 4;
                rimLight.penumbra = 0.5;
                scene.add(rimLight);

                const fillLight = new THREE.PointLight(0xff1133, 0.5);
                fillLight.position.set(5, -2, 5);
                scene.add(fillLight);

                // Mouse Parallax Group
                const ballGroup = new THREE.Group();
                scene.add(ballGroup);

                // --- MATHEMATICAL BOTTOM-RIGHT POSITIONING ---
                function updateBallPosition() {
                    const vFOV = THREE.MathUtils.degToRad(camera.fov);
                    const h = 2 * Math.tan(vFOV / 2) * camera.position.z;
                    const w = h * camera.aspect;
                    // Pin to bottom right: half width minus margin, half height minus margin
                    ballGroup.position.set((w / 2) - 3.5, -(h / 2) + 3.0, 0);
                }
                updateBallPosition();

                // --- PROCEDURAL KOOKABURRA TEXTURE ---
                const texSize = 1024;
                const canvas = document.createElement('canvas');
                canvas.width = texSize;
                canvas.height = texSize / 2;
                const ctx = canvas.getContext('2d');

                ctx.fillStyle = '#630a14';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                for (let i = 0; i < 30000; i++) {
                    const x = Math.random() * canvas.width;
                    const y = Math.random() * canvas.height;
                    ctx.fillStyle = `rgba(0,0,0,${Math.random() * 0.08})`;
                    ctx.fillRect(x, y, 2, 2);
                    ctx.fillStyle = `rgba(255,255,255,${Math.random() * 0.03})`;
                    ctx.fillRect(x+1, y+1, 1, 1);
                }

                const seamY = canvas.height / 2;
                ctx.fillStyle = '#4a050d';
                ctx.fillRect(0, seamY - 8, canvas.width, 16);

                ctx.lineWidth = 2.5;
                ctx.strokeStyle = '#e8e5df';
                ctx.setLineDash([6, 5]); 
                
                const stitchOffsets = [-12, -4, 4, 12];
                stitchOffsets.forEach(offset => {
                    ctx.beginPath();
                    ctx.moveTo(0, seamY + offset);
                    ctx.lineTo(canvas.width, seamY + offset);
                    ctx.stroke();
                });
                
                ctx.setLineDash([]);
                ctx.lineWidth = 1.5;
                for (let x = 0; x < canvas.width; x += 6) {
                    ctx.beginPath();
                    ctx.moveTo(x - 2, seamY - 6);
                    ctx.lineTo(x + 2, seamY + 6);
                    ctx.stroke();
                }

                ctx.fillStyle = '#d4af37'; 
                ctx.font = 'bold 32px "Arial Black", sans-serif';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText('KOOKABURRA', canvas.width / 2, canvas.height / 4);

                const ballTexture = new THREE.CanvasTexture(canvas);
                ballTexture.wrapS = THREE.RepeatWrapping;
                
                // Create Kookaburra Ball Mesh
                const radius = 1.6;
                const geometry = new THREE.SphereGeometry(radius, 128, 128); 
                
                const leatherMaterial = new THREE.MeshPhysicalMaterial({
                    map: ballTexture,
                    bumpMap: ballTexture,
                    bumpScale: 0.015,
                    roughness: 0.65,      
                    metalness: 0.0,       
                    clearcoat: 0.4,       
                    clearcoatRoughness: 0.2,
                    reflectivity: 0.5
                });
                const ball = new THREE.Mesh(geometry, leatherMaterial);
                
                ball.rotation.x = Math.PI / 2.2;
                ball.rotation.y = -Math.PI / 6;
                ball.rotation.z = Math.PI / 2;
                ballGroup.add(ball);

                // --- GSAP Timeline for Scroll ---
                const tl = gsap.timeline({ paused: true });
                
                // On scroll, the ball rolls forward and moves slightly up
                tl.to(ball.rotation, { x: Math.PI * 4, duration: 1, ease: "none" }, 0);
                tl.to(ballGroup.position, { y: ballGroup.position.y + 2, duration: 1, ease: "power1.inOut" }, 0);

                // Scroll Tracking
                const updateScroll = () => {
                    const containers = parentDoc.querySelectorAll('[data-testid="stAppViewContainer"], .main, .stApp');
                    let maxScroll = 0;
                    let currentScroll = 0;
                    
                    containers.forEach(c => {
                        let max = c.scrollHeight - c.clientHeight;
                        if (max > maxScroll) {
                            maxScroll = max;
                            currentScroll = c.scrollTop;
                        }
                    });
                    
                    if (maxScroll === 0) {
                        maxScroll = parentDoc.documentElement.scrollHeight - parentDoc.documentElement.clientHeight;
                        currentScroll = parentDoc.documentElement.scrollTop || window.parent.scrollY;
                    }
                    
                    let progress = 0;
                    if (maxScroll > 0) {
                        progress = currentScroll / maxScroll;
                    } else {
                        // FORCE BALL TO BE VISIBLE AT CENTER IF NO SCROLL POSSIBLE
                        progress = 0.3; 
                    }
                    
                    if (progress < 0) progress = 0;
                    if (progress > 1) progress = 1;
                    
                    tl.progress(progress);
                };

                parentDoc.addEventListener('scroll', updateScroll, { passive: true, capture: true });
                window.parent.addEventListener('scroll', updateScroll, { passive: true, capture: true });
                setTimeout(updateScroll, 100);
                setTimeout(updateScroll, 1000);

                // Mouse Parallax
                const mouse = { x: 0, y: 0, targetX: 0, targetY: 0 };
                window.parent.addEventListener('mousemove', (e) => {
                    mouse.targetX = (e.clientX / window.parent.innerWidth) * 2 - 1;
                    mouse.targetY = -(e.clientY / window.parent.innerHeight) * 2 + 1;
                });

                // Render Loop
                const animate = () => {
                    requestAnimationFrame(animate);
                    mouse.x += (mouse.targetX - mouse.x) * 0.05;
                    mouse.y += (mouse.targetY - mouse.y) * 0.05;
                    ballGroup.position.x = mouse.x * 0.5;
                    ballGroup.position.y = mouse.y * 0.5;
                    ballGroup.rotation.y = mouse.x * 0.2;
                    ballGroup.rotation.x = -mouse.y * 0.2;
                    renderer.render(scene, camera);
                };
                animate();

                // Resize
                window.parent.addEventListener('resize', () => {
                    camera.aspect = window.parent.innerWidth / window.parent.innerHeight;
                    camera.updateProjectionMatrix();
                    renderer.setSize(window.parent.innerWidth, window.parent.innerHeight);
                    if (typeof updateBallPosition === 'function') updateBallPosition();
                    updateScroll();
                });

            } catch (err) {
                console.error("Three.js Error:", err);
            }
        </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=1)
