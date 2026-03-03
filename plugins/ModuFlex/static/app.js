document.addEventListener('DOMContentLoaded', function (_) {
    let snd_log = document.getElementById('send-log')
    let back = document.getElementById('back')
    let аdditional_аccounts = document.getElementById('аdditional-аccounts')

    snd_log.addEventListener('click', function (_) {
        fetch('/ModuFlex/send_logfile', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        }).then(response => console.log(response))
    })

    back.addEventListener('click', function (_) {
        window.location.href = '/'
    })

    аdditional_аccounts.addEventListener('click', function(_) {
        window.location.href = '/ModuFlex/additional_accounts/'
    })
})