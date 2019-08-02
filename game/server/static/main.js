
async function login_submit(){
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    const status = document.getElementById('formstatus');

    let response = await fetch(
        "/login", {
            method: "POST",
            body: JSON.stringify({
                "email": email.value,
                "password": password.value,
            }),
            headers: {
                'Content-Type': 'application/json',
            }
        }
    );

    let json = await response.json();
    switch(json.status){
        case "not found":
            status.innerHTML = "Email address not found";
            email.value = "";
            password.value = "";
            return;
        case "password incorrect":
            status.innerHTML = "Password incorrect";
            password.value = "";
            return;
        case "server error":
            status.innerHTML = "A server error occurred, please retry";
            password.value = "";
            return;
        case "ok":
            window.location = "/"
            break;
        default:
            console.error("invalid status code")
            break;
    }
}

async function register_submit(){
    const email = document.getElementById('email');
    const username = document.getElementById('username');
    const password = document.getElementById('password');
    const password_again = document.getElementById('password_again');
    const status = document.getElementById('formstatus');

    if(password.value != password_again.value){
        status.innerHTML = "Passwords don't match"
        return
    }

    let response = await fetch(
        "/register", {
            method: "POST",
            body: JSON.stringify({
                "email": email.value,
                "username": username.value,
                "password": password.value,
            }),
            headers: {
                'Content-Type': 'application/json',
            }
        }
    );

    let json = await response.json();
    console.log(json)
    switch(json.status){
        case "ok":
            return await login_submit();
        default:
            status.innerHTML = json.status
            break;

    }
}
