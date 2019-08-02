
rgb = (r, g=r, b=g, a=1) => `rgba(${r}, ${g}, ${b}, ${a})`;
print = console.log

window.onload = () => {
    const canvas = document.getElementById("board");
    const ctx = canvas.getContext("2d");
    print(ctx)

    clear = () => {
        ctx.fillStyle = rgb(51);
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    };



    clear();
};


