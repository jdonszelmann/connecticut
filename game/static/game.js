
rgb = (r, g=r, b=g, a=1) => `rgba(${r}, ${g}, ${b}, ${a})`;
print = console.log;
circle = (ctx, x, y, radius) => {
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, 2 * Math.PI);
    ctx.stroke();
}

let socket;
let selected = undefined;
let gridsizex, gridsizey;
let cammove;
let boardsize;

window.onload = () => {
    const canvas = document.getElementById("board");
    const ctx = canvas.getContext("2d");
    boardsize = 13;
    canmove = false;
    gridsizex = canvas.width / boardsize;
    gridsizey = canvas.height / boardsize;
    const circleradius = gridsizex / 3;

    const clear = () => {
        ctx.fillStyle = rgb(51);
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    };

    const drawboard = () => {
        ctx.strokeStyle = rgb(255);
        for (let i = gridsizex/2; i < canvas.width; i += gridsizex) {
            ctx.beginPath();
            ctx.moveTo(0,i);
            ctx.lineTo(canvas.height,i);
            ctx.stroke()
        }
        for (let i = gridsizey/2; i < canvas.height; i += gridsizey){
            ctx.beginPath();
            ctx.moveTo(i,0);
            ctx.lineTo(i, canvas.width);
            ctx.stroke()
        }

        if(selected != undefined){
            const x = Math.floor(selected.x/gridsizex) * gridsizex;
            const y = Math.floor(selected.y/gridsizey) * gridsizey;

            if(canmove){
                ctx.fillStyle = rgb(50,240,50, 0.6);
            }else{
                ctx.fillStyle = rgb(240,50,50, 0.6);
            }
            circle(ctx,x+gridsizex/2, y+gridsizey/2, circleradius);
            ctx.fill();
        }

        for(let coord of coordinates){
            const [x, y, owned] = coord;

            if(owned){
                ctx.fillStyle = rgb(50,240,50, 0.6);
            }else{
                ctx.fillStyle = rgb(240,50,50, 0.6);
            }

            circle(ctx,(x*gridsizex)+gridsizex/2, ((boardsize - y - 1)*gridsizey)+gridsizey/2, circleradius);
            ctx.fill();
        }
    };

    const connection = () => {
        socket = io("/websocket");
        socket.on('connect', function(data) {
            print("socket online")
            socket.emit("startup", data={
                gameid: gamenumber
            })
        });

        socket.on('new_piece', function(data) {
            coordinates.push([data.x, data.y, data.owned]);
            clear();
            drawboard();
        });

        socket.on('should_disconnect', function(data) {
            alert("Your access token expired. Please log in again")
            window.location = "/login"
        });

        socket.on('move_approved', function(data) {
            alert("Move made. wait for your opponent to make one.")
            selected = undefined;
        });

        socket.on('invalid_packet', function(data) {
            alert("You sent an invalid packet. Don't cheat!");
            selected = undefined;
        });

        socket.on('invalid_move', function(data) {
            alert("You can't make that move!");
            selected = undefined;
        });

        socket.on('opponent_offline', function(data) {
            alert("The server detected that your opponent is offline. Please wait.");
            selected = undefined;
        });

        socket.on('no_opponent', function(data) {
            alert("You don't have an opponent yet. Please wait.");
            selected = undefined;
        });

        socket.on('not_your_turn', function(data) {
            alert("It isn't your turn. Wait for your opponent to move.");
            selected = undefined;
        });
    };

    const getMousePos = (e) => {
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;

        return {
            x: (e.clientX - rect.left) * scaleX,
            y: (e.clientY - rect.top) * scaleY
        };
    }

    window.onmousemove = (e) => {
        const pos = getMousePos(e);

        const x = Math.floor(pos.x/gridsizex) * gridsizex;
        const y = Math.floor(pos.y/gridsizey) * gridsizey;

        clear();
        drawboard(13);

        if(canmove){
            ctx.fillStyle = rgb(50,240,50, 0.2);
        }else{
            ctx.fillStyle = rgb(240,50,50, 0.2);
        }
        circle(ctx,x+gridsizex/2, y+gridsizey/2, circleradius);
        ctx.fill();
    };

    window.onmousedown = (e) => {
        newselected = getMousePos(e);

        let oldx, oldy;
        if(selected != undefined){
            oldx = Math.floor(selected.x/gridsizex) * gridsizex;
            oldy = Math.floor(selected.y/gridsizey) * gridsizey;
        }
        const x = Math.floor(newselected.x/gridsizex) * gridsizex;
        const y = Math.floor(newselected.y/gridsizey) * gridsizey;


        if(newselected.x < canvas.width && newselected.y < canvas.height){
            if(selected != undefined && oldx == x && oldy == y){
                selected = undefined;
            }else{
                selected = newselected;
            }
            clear();
            drawboard();
        }
    };
    window.ontouchstart = (e) => window.onmousedown(e);

    connection();
    clear();
    drawboard(13);
};

const move = () => {
    if(selected == undefined){
        return alert("please make a selection first");
    }

    const x = Math.floor(selected.x/gridsizex);
    const y = -Math.floor(selected.y/gridsizey) + (boardsize - 1);

    socket.emit("move", {
        x: x,
        y: y,
        gameid: gamenumber,
    })
};

