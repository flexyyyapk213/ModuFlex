document.addEventListener('DOMContentLoaded', function(e) {
    let back = document.getElementById('back')
    let create_account = document.getElementById('create-additional-account')
    let phone = document.getElementById('phone')
    let password = document.getElementById('password')

    back.addEventListener('click', function(_) {
        window.location.href = '/ModuFlex/'
    })

    create_account.addEventListener('click', function(_) {
        if (phone.value === '') {
            alert('Введите номер телефона(без +)')
            return
        }

        if (phone.value.startsWith('+')) {
            alert('Номер телефона не должен начинаться с +.')
            return
        }

        fetch('/ModuFlex/additional_accounts/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({"phone_number": phone.value, "password": password.value})
        })
        .then(response => {
            if (response.status === 400) {
                return alert('Такой номер телефона уже есть.')
            }
        })

        phone.value = ''
        password.value = ''

        alert('Чтобы изменения внеслись, нужно перезапустить юзербота.')

        update_accounts()
    })

    update_accounts()
})

async function update_accounts() {
    let acc_info = document.getElementById('accounts')

    acc_info.innerHTML = ""
    
    fetch('/ModuFlex/additional_accounts/get_accounts', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => { return response.json() })
    .then(data => {
        data.accounts.forEach((element, i) => {
            let table = document.createElement('div')
            table.classList.add('info-table')
            
            let info = document.createElement('p')
            info.textContent = element.phone_number
            
            let delete_info = document.createElement('button')
            delete_info.textContent = 'Удалить'
            delete_info.classList.add('delete-btn')
            
            delete_info.addEventListener('click', async function(_) {
                fetch(`/ModuFlex/additional_accounts/delete_account=${i}`, {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                }).then(response => console.log(response.status))

                await update_accounts()
            })

            table.appendChild(info)
            table.appendChild(delete_info)

            acc_info.appendChild(table)
        })
    })
}