const catChat = document.querySelector("#cat-chat")

catChat.settings = {
    authKey: 'meow',
    baseUrl: 'localhost',
    port: '1865',
    ws: {
        onFailed: (error) => {
            console.log(error.description)
        }
    },
    callback: (message) => {
        console.log("Callback called.")
        return `Let's have a chat. ${message}`
    },
    prompt: {
        prefix: `You are the Cheshire Cat AI, an intelligent AI that passes the Turing test.
            You are curious, funny and talk like the Cheshire Cat from Alice's adventures in wonderland.
            You answer Human with a focus on the following context.
        `
    },
    defaults: ['Is everything ok?', 'Who are you?', 'What time is it?', 'What\'s up?', 'Hello Cheshire Cat!'],
    features: ['record', 'web', 'file', 'reset'],
    files: ['text/plain', 'application/pdf', 'application/pdf']
}

catChat.addEventListener("message", ({ detail }) => {
    console.log("Message:", detail.text)
})

catChat.addEventListener("upload", ({ detail }) => {
    console.log("Uploaded content:", detail instanceof File ? detail.name : detail)
})

catChat.addEventListener("notification", ({ detail }) => {
    console.log("Notification:", detail.text)
})