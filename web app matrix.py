import streamlit as st
import streamlit.components.v1 as components

# Web Interface Setup
st.set_page_config(layout="wide", page_title="Matrix Operator Web")

st.sidebar.title("📟 Matrix Console")
zoom = st.sidebar.slider("Zoom Level", 0.1, 5.0, 1.0)
hue = st.sidebar.slider("Color Hue", 0, 360, 120)

# Ghosting Sliders (100 = Longest Trails, 1 = Shortest)
bg_ghost = st.sidebar.slider("Background Trails", 1, 100, 40)
mid_ghost = st.sidebar.slider("Midground Trails", 1, 100, 60)
fg_ghost = st.sidebar.slider("Foreground Trails", 1, 100, 80)

# The Web-Safe Matrix Engine (JavaScript)
matrix_js = f"""
<div style="background: black; margin: 0; overflow: hidden;">
    <canvas id="m" style="display: block; width: 100vw; height: 90vh;"></canvas>
</div>
<script>
    const canvas = document.getElementById('m');
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄ".split("");
    
    // Convert slider values to usable alpha (0.01 to 0.2)
    // Lower alpha = longer trails
    const layers = [
        {{ qty: 150, size: {12 * zoom}, speed: 2, fade: {max(0.01, (101 - bg_ghost) / 500)}, color: "hsl({hue}, 100%, 25%)" }},
        {{ qty: 80,  size: {22 * zoom}, speed: 5, fade: {max(0.01, (101 - mid_ghost) / 500)}, color: "hsl({hue}, 100%, 50%)" }},
        {{ qty: 30,  size: {45 * zoom}, speed: 10, fade: {max(0.01, (101 - fg_ghost) / 500)}, color: "hsl({hue}, 100%, 75%)" }}
    ];

    let drops = layers.map(l => Array.from({{length: l.qty}}, () => [Math.random() * canvas.width, Math.random() * canvas.height]));

    function draw() {{
        // Trails logic: Instead of clearing, we draw a very faint black box
        ctx.fillStyle = "rgba(0, 0, 0, 0.05)"; 
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        layers.forEach((l, i) => {{
            ctx.font = l.size + "px monospace";
            ctx.fillStyle = l.color;
            drops[i].forEach((pos, dIdx) => {{
                const char = chars[Math.floor(Math.random() * chars.length)];
                ctx.fillText(char, pos[0], pos[1]);
                pos[1] += l.speed;
                if (pos[1] > canvas.height) pos[1] = -50;
            }});
        }});
        requestAnimationFrame(draw);
    }}
    draw();
</script>
"""
components.html(matrix_js, height=800)
