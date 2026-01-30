document.addEventListener('DOMContentLoaded', function (_) {
    let snd_log = document.getElementById('send-log')
    let back = document.getElementById('back')

    snd_log.addEventListener('click', function (_) {
        fetch('/ModuFlex/send_logfile', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        }).then(response => console.log(response))
    })

    back.addEventListener('click', function (_) {
        window.location.href = '/'
    })
})