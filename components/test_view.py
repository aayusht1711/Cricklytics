import streamlit as st
import streamlit.components.v1 as components

def show_test_view():
    # Inject CSS to make the main container full width and height, and hide default Streamlit elements
    st.markdown("""
        <style>
            /* Reset Streamlit defaults for full screen cinematic experience */
            .block-container {
                padding: 0 !important;
                max-width: 100% !important;
                margin: 0 !important;
                width: 100vw !important;
                height: 100vh !important;
            }
            header {
                display: none !important;
            }
            footer {
                display: none !important;
            }
            /* Make the iframe container take full height */
            iframe {
                height: 100vh !important;
                width: 100vw !important;
                border: none !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Test Cricket Cinematic</title>
        <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700;800&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            :root {
                --forest-green: #0B3D2E;
                --rich-gold: #C9A227;
                --ivory: #F5F0E6;
                --charcoal: #1A1A1A;
                --dark-red: #8B0000;
            }
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                background-color: var(--forest-green);
                color: var(--ivory);
                font-family: 'Inter', sans-serif;
                overflow-x: hidden;
                /* Background stadium effect */
                background-image: radial-gradient(circle at center, rgba(11, 61, 46, 0.8) 0%, rgba(26, 26, 26, 1) 100%);
                background-attachment: fixed;
            }
            
            h1, h2, h3, h4, h5 { font-family: 'Cinzel', serif; color: var(--rich-gold); text-transform: uppercase; }
            
            /* Custom Scrollbar */
            ::-webkit-scrollbar { width: 8px; }
            ::-webkit-scrollbar-track { background: var(--charcoal); }
            ::-webkit-scrollbar-thumb { background: var(--rich-gold); border-radius: 4px; }
            
            /* Video Overlay */
            #intro-video {
                position: fixed;
                top: 0; left: 0; width: 100vw; height: 100vh;
                object-fit: cover;
                z-index: 9999;
                transition: opacity 2s ease-in-out;
                background-color: #000;
            }
            
            /* Dashboard Container */
            .dashboard-container {
                opacity: 0;
                transition: opacity 3s ease-in-out;
                position: relative;
                z-index: 10;
                width: 100%;
                padding: 4rem 2rem;
            }
            
            /* Hero Section */
            .hero-section {
                height: 90vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                position: relative;
                margin-bottom: 4rem;
            }
            
            .hero-title {
                font-size: 5rem;
                font-weight: 800;
                text-shadow: 0 10px 30px rgba(0,0,0,0.8);
                margin-bottom: 1rem;
                letter-spacing: 4px;
                animation: fadeInUp 2s ease-out forwards;
                opacity: 0;
            }
            
            .hero-subtitle {
                font-size: 1.5rem;
                font-weight: 300;
                letter-spacing: 2px;
                color: var(--ivory);
                animation: fadeInUp 2s ease-out 0.5s forwards;
                opacity: 0;
            }
            
            /* Red Ball Animation */
            .cricket-ball {
                width: 50px;
                height: 50px;
                background: radial-gradient(circle at 30% 30%, #ff4d4d, var(--dark-red));
                border-radius: 50%;
                margin: 3rem auto;
                box-shadow: inset -10px -10px 20px rgba(0,0,0,0.5), 0 15px 25px rgba(0,0,0,0.6);
                animation: rotateBall 10s linear infinite, bounceBall 3s ease-in-out infinite alternate;
                position: relative;
            }
            .cricket-ball::after {
                content: '';
                position: absolute;
                top: 50%;
                left: 0;
                width: 100%;
                height: 2px;
                background: #fff;
                box-shadow: 0 1px 2px rgba(0,0,0,0.5);
                transform: translateY(-50%);
            }
            
            @keyframes rotateBall { 100% { transform: rotate(360deg); } }
            @keyframes bounceBall { 100% { transform: translateY(-20px); } }
            @keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
            
            /* Layout Grid */
            .grid-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 2rem;
                max-width: 1400px;
                margin: 0 auto;
            }
            
            /* Glassmorphism Cards */
            .glass-card {
                background: rgba(255, 255, 255, 0.03);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid rgba(201, 162, 39, 0.2);
                border-radius: 16px;
                padding: 2rem;
                box-shadow: 0 20px 40px rgba(0,0,0,0.4);
                transition: transform 0.4s ease, border-color 0.4s ease;
            }
            .glass-card:hover {
                transform: translateY(-10px);
                border-color: var(--rich-gold);
            }
            
            .glass-card h3 {
                border-bottom: 1px solid rgba(201, 162, 39, 0.3);
                padding-bottom: 1rem;
                margin-bottom: 1.5rem;
                font-size: 1.8rem;
            }
            
            /* Specific Section Styles */
            /* Live Match Center */
            .live-score { font-size: 3rem; font-weight: bold; margin: 1rem 0; font-family: 'Cinzel', serif;}
            .team-vs { display: flex; justify-content: space-between; align-items: center; font-size: 1.5rem; }
            .badge { background: var(--dark-red); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; letter-spacing: 1px; text-transform: uppercase; }
            
            /* Session Analytics */
            .session-row { display: flex; justify-content: space-between; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); }
            
            /* Timeline (Match Story) */
            .timeline { border-left: 2px solid var(--rich-gold); padding-left: 2rem; margin-left: 1rem; }
            .timeline-item { position: relative; margin-bottom: 2rem; }
            .timeline-item::before {
                content: '';
                position: absolute;
                left: -2.45rem;
                top: 5px;
                width: 16px;
                height: 16px;
                background: var(--dark-red);
                border: 2px solid var(--rich-gold);
                border-radius: 50%;
            }
            .timeline-date { color: var(--rich-gold); font-weight: bold; margin-bottom: 0.5rem; }
            
            /* Conditions Center */
            .weather-icon { font-size: 2.5rem; margin-bottom: 1rem; color: var(--ivory); }
            
            /* Player Battle */
            .battle-row { display: flex; justify-content: space-between; align-items: center; margin: 10px 0; }
            .bar-bg { width: 40%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; }
            .bar-fill { height: 100%; background: var(--rich-gold); border-radius: 4px; }
            
            /* Legends */
            .legend-card { text-align: center; }
            .legend-img { width: 120px; height: 120px; border-radius: 50%; border: 3px solid var(--rich-gold); margin: 0 auto 1rem; background: var(--charcoal); object-fit: cover; }
            
        </style>
    </head>
    <body>

        <!-- Intro Video -->
        <video id="intro-video" autoplay muted>
            <!-- Streamlit serves static files from /app/static -->
            <source src="/app/static/the_test_cricket.mp4" type="video/mp4">
            Your browser does not support the video tag.
        </video>
        
        <script>
            // Collapse Streamlit Sidebar automatically
            try {
                const closeBtn = window.parent.document.querySelector('[data-testid="stSidebarCollapseButton"]');
                if (closeBtn) closeBtn.click();
            } catch (e) { console.log("Could not collapse sidebar", e); }
        </script>

        <div class="dashboard-container" id="dashboard">
            
            <!-- Hero Section -->
            <div class="hero-section">
                <h1 class="hero-title">The Ultimate Test Cricket Experience</h1>
                <p class="hero-subtitle">Five Days. Endless Stories. Cricket In Its Purest Form.</p>
                <div class="cricket-ball"></div>
                <div style="position:absolute; bottom: 2rem; animation: bounceBall 2s infinite;">
                    <span style="color:var(--rich-gold); font-size: 1.5rem;">↓</span>
                </div>
            </div>

            <!-- Main Layout Grid -->
            <div class="grid-container">
                
                <!-- SECTION 1: LIVE MATCH CENTER -->
                <div class="glass-card" style="grid-column: 1 / -1;">
                    <div style="display:flex; justify-content: space-between;">
                        <h3>Live Match Center</h3>
                        <span class="badge">Day 4 - Session 2</span>
                    </div>
                    <div class="team-vs">
                        <span>INDIA <br><span style="font-size:1rem; color: #ccc;">345 & 120/3</span></span>
                        <div style="text-align:center;">
                            <div class="live-score">Target: 320</div>
                            <span style="color: var(--rich-gold);">Overs: 42.4 | RR: 2.83</span>
                        </div>
                        <span style="text-align:right;">AUSTRALIA <br><span style="font-size:1rem; color: #ccc;">280 & 184</span></span>
                    </div>
                    <div style="margin-top: 2rem; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 1rem; display: flex; justify-content: space-around;">
                        <div style="text-align:center;"><strong>Partnership</strong><br>45 (98)</div>
                        <div style="text-align:center;"><strong>Win Probability</strong><br><span style="color:#C9A227;">IND 62%</span> - AUS 38%</div>
                        <div style="text-align:center;"><strong>Match Situation</strong><br>India needs 200 runs to win</div>
                    </div>
                </div>

                <!-- SECTION 2: SESSION ANALYTICS -->
                <div class="glass-card">
                    <h3>Session Analytics</h3>
                    <div class="session-row">
                        <div>
                            <div style="color:var(--rich-gold); font-weight:bold;">Morning Session</div>
                            <div style="font-size:0.9rem; color:#aaa;">28 Overs</div>
                        </div>
                        <div style="text-align:right;">
                            <div>72 Runs / 2 Wkts</div>
                            <div style="color:var(--dark-red); font-size:0.8rem;">Session: AUS</div>
                        </div>
                    </div>
                    <div class="session-row">
                        <div>
                            <div style="color:var(--rich-gold); font-weight:bold;">Afternoon Session</div>
                            <div style="font-size:0.9rem; color:#aaa;">32 Overs</div>
                        </div>
                        <div style="text-align:right;">
                            <div>95 Runs / 1 Wkt</div>
                            <div style="color:#C9A227; font-size:0.8rem;">Session: IND</div>
                        </div>
                    </div>
                    <div class="session-row" style="border:none; margin:0; padding:0;">
                        <div>
                            <div style="color:var(--rich-gold); font-weight:bold;">Evening Session</div>
                            <div style="font-size:0.9rem; color:#aaa;">14.4 Overs</div>
                        </div>
                        <div style="text-align:right;">
                            <div>48 Runs / 0 Wkt</div>
                            <div style="color:#C9A227; font-size:0.8rem;">Session: IND (Ongoing)</div>
                        </div>
                    </div>
                </div>

                <!-- SECTION 3: BATTLE ZONE -->
                <div class="glass-card">
                    <h3>Battle Zone</h3>
                    <div style="text-align:center; font-family:'Cinzel', serif; font-size: 1.2rem; margin-bottom: 1rem;">
                        V. Kohli <span style="color:var(--dark-red);">vs</span> P. Cummins
                    </div>
                    <div class="battle-row">
                        <span>Runs Scored</span>
                        <div style="flex-grow:1; margin: 0 15px; display:flex; align-items:center;">
                            <div class="bar-bg" style="width:100%; display:flex;">
                                <div class="bar-fill" style="width:65%;"></div>
                            </div>
                        </div>
                        <span>82</span>
                    </div>
                    <div class="battle-row">
                        <span>Balls Faced</span>
                        <div style="flex-grow:1; margin: 0 15px; display:flex; align-items:center;">
                            <div class="bar-bg" style="width:100%; display:flex;">
                                <div class="bar-fill" style="width:100%; background:var(--forest-green); border:1px solid var(--rich-gold);"></div>
                            </div>
                        </div>
                        <span>145</span>
                    </div>
                    <div class="battle-row">
                        <span>Dismissals</span>
                        <div style="flex-grow:1; margin: 0 15px; display:flex; align-items:center;">
                            <div class="bar-bg" style="width:100%; display:flex;">
                                <div class="bar-fill" style="width:20%; background:var(--dark-red);"></div>
                            </div>
                        </div>
                        <span>4</span>
                    </div>
                    <div class="battle-row">
                        <span>Dot Ball %</span>
                        <div style="flex-grow:1; margin: 0 15px; display:flex; align-items:center;">
                            <div class="bar-bg" style="width:100%; display:flex;">
                                <div class="bar-fill" style="width:78%; background:#ccc;"></div>
                            </div>
                        </div>
                        <span>78%</span>
                    </div>
                </div>

                <!-- SECTION 4: MATCH STORY -->
                <div class="glass-card" style="grid-column: 1 / -1;">
                    <h3>Cinematic Match Story</h3>
                    <div class="timeline">
                        <div class="timeline-item">
                            <div class="timeline-date">DAY 1 - The First Strike</div>
                            <p>Australia elects to bat under overcast skies. Bumrah produces a masterclass opening spell, dismissing the openers within the first 10 overs. Smith anchors the innings.</p>
                        </div>
                        <div class="timeline-item">
                            <div class="timeline-date">DAY 2 - The Resistance</div>
                            <p>Australia bowled out for 280. India starts strong but loses quick wickets to Lyon's spin. Pant counter-attacks with a brilliant 85, bringing India back into the game.</p>
                        </div>
                        <div class="timeline-item">
                            <div class="timeline-date">DAY 3 - The Turning Point</div>
                            <p>India takes a crucial 65-run lead. Australia's second innings is rocky, but a historic 120-run partnership for the 7th wicket sets a challenging target of 320 for India.</p>
                        </div>
                        <div class="timeline-item" style="margin-bottom:0;">
                            <div class="timeline-date">DAY 4 - The Final Frontier (Live)</div>
                            <p>India loses early wickets, but the middle order stabilizes. The tension is palpable as the shadows lengthen. This is Test cricket at its absolute pinnacle.</p>
                        </div>
                    </div>
                </div>

                <!-- SECTION 5: CONDITIONS CENTER -->
                <div class="glass-card">
                    <h3>Conditions Center</h3>
                    <div style="display:flex; justify-content: space-around; text-align:center; margin-bottom: 2rem;">
                        <div>
                            <div class="weather-icon">⛅</div>
                            <div>24°C<br><span style="font-size:0.8rem; color:#aaa;">Temp</span></div>
                        </div>
                        <div>
                            <div class="weather-icon">💧</div>
                            <div>65%<br><span style="font-size:0.8rem; color:#aaa;">Humidity</span></div>
                        </div>
                        <div>
                            <div class="weather-icon">☁️</div>
                            <div>40%<br><span style="font-size:0.8rem; color:#aaa;">Cloud Cover</span></div>
                        </div>
                    </div>
                    <h4 style="font-size:1rem; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:5px; margin-bottom:10px;">Pitch Evolution</h4>
                    <ul style="list-style:none; line-height: 1.8; font-size:0.9rem;">
                        <li><span style="color:var(--rich-gold);">Day 1:</span> Fresh, assisting seamers</li>
                        <li><span style="color:var(--rich-gold);">Day 2:</span> Flattened out, good for batting</li>
                        <li><span style="color:var(--rich-gold);">Day 3:</span> Some variable bounce</li>
                        <li><span style="color:var(--dark-red);">Day 4:</span> Significant turn & cracks opening</li>
                    </ul>
                </div>

                <!-- SECTION 6: MOMENTUM CENTER -->
                <div class="glass-card">
                    <h3>Momentum Center</h3>
                    <p style="font-size:0.9rem; color:#aaa; margin-bottom:1rem;">Match Momentum Swing (Last 30 Overs)</p>
                    <svg viewBox="0 0 400 150" style="width:100%; height:auto; overflow:visible;">
                        <path d="M 0,75 L 50,40 L 100,90 L 150,60 L 200,80 L 250,30 L 300,50 L 350,110 L 400,20" 
                              fill="none" stroke="var(--rich-gold)" stroke-width="4" stroke-linejoin="round"/>
                        <path d="M 0,75 L 50,40 L 100,90 L 150,60 L 200,80 L 250,30 L 300,50 L 350,110 L 400,20 L 400,150 L 0,150 Z" 
                              fill="rgba(201, 162, 39, 0.1)" />
                        <!-- 50% baseline -->
                        <line x1="0" y1="75" x2="400" y2="75" stroke="rgba(255,255,255,0.2)" stroke-width="2" stroke-dasharray="5,5"/>
                    </svg>
                    <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-top:10px;">
                        <span>Session 1</span>
                        <span>Session 2</span>
                        <span>Now</span>
                    </div>
                </div>

                <!-- SECTION 7 & 8: LEGENDS & RECORDS -->
                <div class="glass-card" style="grid-column: 1 / -1; margin-bottom:4rem;">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap;">
                        <div style="flex: 1 1 45%; min-width:300px; padding-right:2rem;">
                            <h3>Legends of Test Cricket</h3>
                            <div style="display:flex; justify-content:space-around; margin-top:2rem;">
                                <div class="legend-card">
                                    <div class="legend-img" style="background-image:url('https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80'); background-size:cover;"></div>
                                    <h4>D. Bradman</h4>
                                    <p style="font-size:0.9rem; color:#aaa;">Avg: 99.94</p>
                                </div>
                                <div class="legend-card">
                                    <div class="legend-img" style="background-image:url('https://images.unsplash.com/photo-1593341646782-e0b495cff86d?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80'); background-size:cover;"></div>
                                    <h4>S. Tendulkar</h4>
                                    <p style="font-size:0.9rem; color:#aaa;">Runs: 15,921</p>
                                </div>
                            </div>
                        </div>
                        <div style="flex: 1 1 45%; min-width:300px;">
                            <h3>Historical Records</h3>
                            <ul style="list-style:none; line-height: 2.2;">
                                <li><span style="color:var(--rich-gold);">Highest Score:</span> B. Lara (400*)</li>
                                <li><span style="color:var(--rich-gold);">Best Bowling:</span> J. Laker (10/53)</li>
                                <li><span style="color:var(--rich-gold);">Most Wickets:</span> M. Muralitharan (800)</li>
                                <li><span style="color:var(--rich-gold);">Most Centuries:</span> S. Tendulkar (51)</li>
                                <li><span style="color:var(--rich-gold);">Longest Match:</span> Timeless Test (10 Days)</li>
                            </ul>
                        </div>
                    </div>
                </div>

            </div>
        </div>

        <script>
            // Video transition logic
            const video = document.getElementById('intro-video');
            const dashboard = document.getElementById('dashboard');

            // Handle video error (e.g. file not found)
            video.addEventListener('error', () => {
                video.style.display = 'none';
                dashboard.style.opacity = '1';
            });

            // When video ends, fade it out and show dashboard
            video.addEventListener('ended', () => {
                video.style.opacity = '0';
                dashboard.style.opacity = '1';
                setTimeout(() => {
                    video.remove(); // Remove completely after transition
                }, 2000);
            });

            // If user clicks, skip video
            video.addEventListener('click', () => {
                video.style.opacity = '0';
                dashboard.style.opacity = '1';
                setTimeout(() => {
                    video.remove();
                }, 2000);
            });
            
            // Allow video to autoplay in some strict browsers by ensuring it plays
            video.play().catch(e => console.log("Autoplay blocked:", e));
        </script>
    </body>
    </html>
    """
    
    # Render HTML in an iframe with no fixed height, let CSS handle it
    components.html(html_code, scrolling=True)
