import styles from './styles.js';


class Widget {
    constructor({position = 'bottom-right'} = {}) {
        this.position = this.getPosition(position); //{ bottom: '30px', right: '30px'}
        this.open = false;
        this.initalise();
        this.createStyles();
    }

    getPosition(position) {
        const [vertical, horizontal] = position.split('-')
        return {
            [vertical]: '30px',
            [horizontal]: '30px'
        }
    }

    initalise() {
        const container = document.createElement('div');
        container.style.position = 'fixed';
        container.style.zIndex = '1000';
        Object.keys(this.position).forEach(
            key => container.style[key] = this.position[key]);
        document.body.appendChild(container)

        const buttonContainer = document.createElement('div');
        buttonContainer.classList.add('button-container');
        // buttonContainer.innerHTML = 'Prenota/Book a Table'
        buttonContainer.addEventListener('click', this.toggleOpen.bind(this));
        const widgetText = document.createElement('div');
        widgetText.innerHTML = 'Prenota/Book a Table'
        widgetText.classList.add('widget-text');
        this.widgetText = widgetText
        const icon = document.createElement('img');
        icon.src = 'https://sistema.ristaiuto.it/static/images/favicon.ico';
        icon.classList.add('icon');
        this.icon = icon;
        buttonContainer.appendChild(this.icon);
        buttonContainer.appendChild(this.widgetText);

        this.messageContainer = document.createElement('div');
        this.messageContainer.classList.add('hidden', 'message-container');

        this.createMessageContainerContent();

        container.appendChild(this.messageContainer);
        container.appendChild(buttonContainer);

        document.addEventListener('click', this.closeOnOutsideClick.bind(this));

    }

    createMessageContainerContent() {
        this.messageContainer.innerHTML = '';
        const title = document.createElement('h2');
        title.textContent = `For which date do you want to reserve a table?`;

        const form = document.createElement('form');
        form.classList.add('content');
        const dateInput = document.createElement('input');
        dateInput.required = true;
        dateInput.id = 'date';
        dateInput.type = 'date'; // Change type to text for the datepicker to work
        dateInput.placeholder = 'Select a date';

        const numberOfPersonsInput = document.createElement('input');
        numberOfPersonsInput.required = true;
        numberOfPersonsInput.id = 'numberOfPersons';
        numberOfPersonsInput.type = 'number'; // Change type to text for the datepicker to work
        numberOfPersonsInput.placeholder = 'Select number of persons';

        form.appendChild(dateInput);
        form.appendChild(numberOfPersonsInput);

        const btn = document.createElement('button');
        btn.textContent = 'Submit';
        form.appendChild(btn);
        form.addEventListener('submit', this.submitDateAndPersons.bind(this));

        this.messageContainer.appendChild(title);
        this.messageContainer.appendChild(form);

    }

    createStyles() {
        const styleTag = document.createElement('style');
        styleTag.innerHTML = styles;
        document.head.appendChild(styleTag);
    }

    toggleOpen() {
        this.open = !this.open;
        if (this.open) {
            this.messageContainer.classList.remove('hidden');
        } else {
            this.createMessageContainerContent();
            this.messageContainer.classList.add('hidden');
        }
    }

    closeOnOutsideClick(event) {
        // Check if the clicked element is outside the widget
        if (!this.messageContainer.contains(event.target) && !this.widgetText.contains(event.target)) {
            // Close the widget
            this.open = false;
            this.createMessageContainerContent();
            this.messageContainer.classList.add('hidden');
            document.removeEventListener('click', this.closeOnOutsideClick.bind(this));
        }
    }

    submitDateAndPersons(event) {
        event.preventDefault();
        const dateFormSubmission = {
            date: event.srcElement.querySelector('#date').value,
            numberOfPersons: event.srcElement.querySelector('#numberOfPersons').value,
        };
        const scriptTag = document.querySelector('#widgetScript');
        const restaurantSqid = scriptTag.dataset.restaurantSqid;
        const data = {date: dateFormSubmission.date, numberOfPersons: dateFormSubmission.numberOfPersons};
        const reservationDate = data.date.toString()
        console.log('submit date and persons')

        // https://sistema.ristaiuto.it/check_availability?restaurantID=1&reservation_date=2023-11-11&number_of_persons=4
        const url = `http://127.0.0.1:8000/check_availability?restaurantSQID=${restaurantSqid}&reservation_date=${reservationDate}&number_of_persons=${data.numberOfPersons}`
        fetch(url, {
            method: 'GET',
            headers: {'Content-Type': 'application/json',},
        }).then(response => response.json())
            .then(responseData => {
                this.messageContainer.innerHTML = '';
                const availableTimesForm = document.createElement('form');
                availableTimesForm.classList.add('time-buttons-content')

                responseData.available_times.forEach(time => {
                    const listItem = document.createElement('a');
                    listItem.classList.add('available-time-a')
                    listItem.textContent = time;
                    listItem.addEventListener('click', () => this.toggleSelected(listItem, time));
                    availableTimesForm.appendChild(listItem);
                });

                const btn = document.createElement('button');
                btn.textContent = 'Submit';
                btn.classList.add('submit-time-button')
                availableTimesForm.appendChild(btn);

                availableTimesForm.addEventListener('submit', () => this.submitTimeForm(restaurantSqid, reservationDate, data.numberOfPersons));
                this.messageContainer.innerHTML = '<h2>Choose a Time:</h2>';
                this.messageContainer.appendChild(availableTimesForm);

            }).catch(error => {
            console.error('Error:', error);
        });
    }

    submitTimeForm(restaurantSqid, reservationDate, numberOfPersons) {
        console.log('ASDFASDFSDAFSDFASDF', restaurantSqid, reservationDate, this.selectedTime)
        this.messageContainer.innerHTML = '<h2>Fill in Contact info:</h2>';
        const url = `http://127.0.0.1:8000/make_reservation?restaurantSQID=${restaurantSqid}&reservation_date=${reservationDate}&number_of_persons=${numberOfPersons}&reservation_time=${this.selectedTime}`
        fetch(url, {
            method: 'GET',
            headers: {'Content-Type': 'application/json',},
        }).then(response => response.json())
            .then(responseData => {
                console.log('held reservation', responseData.held_reservation_id)
                this.messageContainer.innerHTML = '';
                if (responseData.status === 'possible_reservation_found') {
                    this.messageContainer.innerHTML = '<h2>Fill in Contact Details</h2>';
                    const contactInfoForm = document.createElement('form');
                    contactInfoForm.classList.add('content')

                    const nameInput = document.createElement('input');
                    nameInput.required = true;
                    nameInput.id = 'nameInput';
                    nameInput.type = 'text';
                    nameInput.placeholder = 'Fill in name';

                    const emailInput = document.createElement('input');
                    emailInput.required = true;
                    emailInput.id = 'emailInput';
                    emailInput.type = 'text'; // Change type to text for the datepicker to work
                    emailInput.placeholder = 'Fill in email';

                    const telephoneInput = document.createElement('input');
                    telephoneInput.required = true;
                    telephoneInput.id = 'telephoneInput';
                    telephoneInput.type = 'text';
                    telephoneInput.placeholder = 'telephone number';

                    const btn = document.createElement('button');
                    btn.textContent = 'Submit';
                    btn.classList.add('submit-time-button')

                    contactInfoForm.appendChild(nameInput)
                    contactInfoForm.appendChild(emailInput)
                    contactInfoForm.appendChild(telephoneInput)
                    contactInfoForm.appendChild(btn);
                    contactInfoForm.addEventListener('submit', (event) => this.submitContactInfo(event, responseData.held_reservation_id));

                    this.messageContainer.appendChild(contactInfoForm)

                }

            }).catch(error => {
            console.error('Error:', error);
            this.messageContainer.innerHTML = '<h2>Error</h2>';
        });
    }

    submitContactInfo(event, responseData) {
        console.log('event', event)
        console.log('submit contact info', responseData)
        // reservationID, name, email, telephone_nr
        // const url = `http://127.0.0.1:8000/confirm_booking?restaurantSQID=${restaurantSqid}&reservation_date=${reservationDate}&number_of_persons=${numberOfPersons}&reservation_time=${this.selectedTime}`

        this.messageContainer.innerHTML = '<h2>Reservation made</h2>';
    }

    toggleSelected(selectedItem, time) {
        // Reset color for all items
        document.querySelectorAll('.available-time-a').forEach(item => item.classList.remove('selected'));
        // Set color for the selected item
        selectedItem.classList.add('selected');
        // Store the selected time in a property or variable
        this.selectedTime = time;
    }
}


export {Widget}