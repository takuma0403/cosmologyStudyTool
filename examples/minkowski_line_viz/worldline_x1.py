"""x=1 世界線のミンコフスキー図サンプル。"""

from minkowski_line_viz import MinkowskiLineConfig, animate_frame_correction, plot_minkowski_line

cfg = MinkowskiLineConfig(beta=0.6, x_const=1.0)

# 静止図
fig = plot_minkowski_line(config=cfg)
fig.savefig("examples/minkowski_line_viz/dist/worldline_x1_static.png", dpi=120)
print("Saved: worldline_x1_static.png")

# アニメーション（S フレーム → S' フレーム補正）
anim = animate_frame_correction(config=cfg, frames=60)
anim.save("examples/minkowski_line_viz/dist/worldline_x1_correction.gif", writer="pillow", fps=cfg.fps)
print("Saved: worldline_x1_correction.gif")
