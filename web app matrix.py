import streamlit as st
import streamlit.components.v1 as components

# --- WEB UI SETUP ---
st.set_page_config(layout="wide", page_title="Matrix Operator Web")

st.sidebar.title("📟 Matrix Console")

# Optics
with st.sidebar.expander("OPTICS", expanded=True):
    zoom = st.slider("Zoom Level", 0.1, 5.0, 1.0)
    hue = st.slider("Color Hue", 0, 360, 120)

# Ghosting
with st.sidebar.expander("TRAILS (GHOSTING)"):
    bg_ghost = st.slider("BG Trails", 0, 100, 40)
    mid_ghost = st.slider("MID Trails", 0, 100, 60)
    fg_ghost = st.slider("FG Trails", 0, 100, 80)

# Speed Controls
with st.sidebar.expander("VELOCITY (SPEED)"):
    bg_speed = st.slider("Background Speed", 0.1, 10.0, 2.0)
    mid_speed = st.slider("Midground Speed", 0.1, 10.0, 5.0)
    fg_speed = st.slider("Foreground Speed", 0.1, 10.0, 8.0)

# --- THE ENGINE ---
matrix_js = f"""
<body style="margin:0; background:black; overflow:hidden;">
    <canvas id="m"></canvas>
    <script>
        const canvas = document.getElementById('m');
        const ctx = canvas.getContext('2d');

        function resize() {{
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }}
        window.onresize = resize;
        resize();

        const chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄ".split("");

        const layers = [
            {{ qty: 150, size: {12 * zoom}, speed: {bg_speed}, fade: {max(0.01, (101 - bg_ghost) / 400)}, color: "hsl({hue}, 100%, 25%)" }},
            {{ qty: 80,  size: {22 * zoom}, speed: {mid_speed}, fade: {max(0.01, (101 - mid_ghost) / 400)}, color: "hsl({hue}, 100%, 50%)" }},
            {{ qty: 30,  size: {45 * zoom}, speed: {fg_speed}, fade: {max(0.01, (101 - fg_ghost) / 400)}, color: "hsl({hue}, 100%, 75%)" }}
        ];

        let drops = layers.map(l => Array.from({{length: l.qty}}, () => [Math.random() * canvas.width, Math.random() * canvas.height]));

        function draw() {{
            // Trails logic
            ctx.fillStyle = "rgba(0, 0, 0, 0.05)"; 
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            layers.forEach((l, i) => {{
                ctx.font = l.size + "px monospace";
                ctx.fillStyle = l.color;
                drops[i].forEach((pos, dIdx) => {{
                    const char = chars[Math.floor(Math.random() * chars.length)];
                    ctx.fillText(char, pos[0], pos[1]);

                    // Apply the new speed sliders here
                    pos[1] += l.speed;

                    if (pos[1] > canvas.height) pos[1] = -50;
                }});
            }});
            requestAnimationFrame(draw);
        }}
        draw();
    </script>
</body>
"""
components.html(matrix_js, height=1000)
