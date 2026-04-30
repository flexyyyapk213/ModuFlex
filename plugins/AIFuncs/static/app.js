var offset = 0

document.addEventListener('DOMContentLoaded', async function(e) {
    let send = document.getElementById('send-message')
    let input = document.getElementById('input-ai')

    send.addEventListener('click', function(_) {
        console.log(offset)
        if (input.value === '') {
            alert('Введите текст.')
            return
        }
        
        fetch('/AIFuncs/send_message', {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({text: input.value})
        })

        offset += 1

        const history = document.getElementById('history')
        const message = document.createElement('div')

        message.classList.add("user")
        message.textContent = input.value

        history.appendChild(message)

        history.scrollTo({
            top: history.scrollHeight,
            behavior: 'smooth'
        });


        input.value = ''
    })

    updates_history(offset)
})

async function updates_history() {
    try {
        const response = await fetch(`/AIFuncs/get_message=${offset}`)
        
        if (response.status !== 200) {
            setTimeout(() => updates_history(), 5000)
            return
        }

        const data = await response.json();
        const history = document.getElementById('history')
        const message = document.createElement('div')
        message.classList.add(data.history.role === "user" ? "user" : "ai")

        const raw = data.history.content ?? '';
        const unsafeHtml = marked.parse(raw);
        const safeHtml = DOMPurify.sanitize(unsafeHtml);

        message.innerHTML = safeHtml;
        message.querySelectorAll('pre code').forEach((el) => {
            hljs.highlightElement(el);
        });

        message.querySelectorAll('pre').forEach((el) => {
            const copy = document.createElement('button')
            copy.classList.add('copy-code')

            copy.addEventListener('click', function(_) {
                copyTextToClipboard(el.textContent)
            })

            el.appendChild(copy)
        })

        history.appendChild(message)
        history.scrollTo({
            top: history.scrollHeight,
            behavior: 'smooth'
        });

        offset += 1

        updates_history()

    } catch (err) {
        setTimeout(() => updates_history(), 5000)
    }
}

function execCommandCopy(text) {
    const temp = document.createElement("textarea");
    temp.value = text;
    temp.style.cssText = "position: absolute; left: -9999px; top: -9999px";
    document.body.appendChild(temp);
    temp.select();
    temp.setSelectionRange(0, 99999);

    const success = document.execCommand("copy");
    document.body.removeChild(temp);
    return success;
}

function copyTextToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
    return navigator.clipboard
        .writeText(text)
        .then(() => true)
        .catch(() => execCommandCopy(text));
    }
    return execCommandCopy(text);
}