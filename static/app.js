document.addEventListener('DOMContentLoaded', function (e) {
    let cursor = document.getElementById('typing-text')
    let texts = [
        'ModuFlex...',
        'Модульный',
        'Быстрый',
        'Web Interface',
        'Гибкость',
        'Автоматизация',
        'Плагины',
        'Расширяемость',
        'Модули',
        'Современный',
        'Асинхронный',
        'API',
        'Панель управления',
        'Лёгкость',
        'Простота',
        'Доступность',
        'Боты',
        'UI/UX',
        'Удобство',
        'Многофункциональность',
        'Надёжность',
        'Главная страница',
        'AI',
        'v0.1.0b2',
        'ЮзерБот',
        'MF',
        'Синхронный',
        'Мультиаккаунт'
    ]
    let currentText = getRandomInt(0, texts.length - 1)
    let currentIndex = 0

    const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    fetch('/get_plugins', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    }).then(response => { return response.json() }).then(data => {
        let plugins = data.plugins

        let plgs = document.querySelector('.plugins')

        plugins.forEach(plugin => {
            texts.push(plugin)

            let btn = document.createElement('button')
            btn.classList.add('btn-glass')

            btn.textContent = plugin

            btn.addEventListener('click', function (_e) {
                window.location.href = '/' + plugin + '/'
            })

            plgs.appendChild(btn)
        })
    })

    async function typing() {
        while (true) {
            while (currentIndex !== texts[currentText].length) {
                writeText(texts[currentText][currentIndex])

                currentIndex += 1

                await wait(getRandomInt(20, 500))
            }

            await wait(2000)

            while (cursor.textContent.length > 0) {
                cursor.textContent = cursor.textContent.slice(0, cursor.textContent.length - 1)

                await wait(100)
            }

            currentIndex = 0
            while (true) {
                let newText = getRandomInt(0, texts.length - 1)
                if (newText === currentText) {
                    continue
                }
                currentText = newText
                break
            }
        }
    }

    function writeText(sumb) {
        cursor.textContent += sumb
    }

    typing()
})

function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}