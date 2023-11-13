class Widget {
    constructor({position = 'bottom-right'} = {}) {
        console.log('loaded')
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
        icon.src = '/static/images/favicon.ico';
        icon.classList.add('icon');
        this.icon = icon;
        buttonContainer.appendChild(this.icon);
        buttonContainer.appendChild(this.widgetText);

        this.messageContainer = document.createElement('div');
        this.messageContainer.classList.add('hidden', 'message-container');

        this.createMessageContainerContent();

        container.appendChild(this.messageContainer);
        container.appendChild(buttonContainer);
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
        dateInput.type = 'text'; // Change type to text for the datepicker to work
        dateInput.placeholder = 'Select a date';
        form.appendChild(dateInput);

        // Initialize jQuery datepicker
        // $(dateInput).datepicker();

        const btn = document.createElement('button');
        btn.textContent = 'Submit';
        form.appendChild(btn);
        form.addEventListener('submit', this.submit.bind(this));

        this.messageContainer.appendChild(title);
        this.messageContainer.appendChild(form);

    }

    createStyles() {
        const styleTag = document.createElement('style');
        styleTag.innerHTML = `
            .button-container {
                background-color: #04b73f;
                display: flex;
                align-items: center;
                width: 200px;
                text-align: center;
                height: 75px;
                border-radius: 25px;
                border: 4px solid #e8701a;
                background: #e2e2e2e2;
                box-shadow: rgba(0, 0, 0, .2) 0 3px 5px -1px,rgba(0, 0, 0, .14) 0 6px 10px 0,rgba(0, 0, 0, .12) 0 1px 18px 0;
                cursor: pointer;
            }
            .icon {
                cursor: pointer;
                transition: transform .3s ease;
            }
            .widget-text {
                font-family: Monaco, serif;
                font-weight: lighter;
                color: black;
                font-size: 19px;
                line-height: normal;
                margin-left: -10px; 
            }
            .hidden {
                transform: scale(0);
            }

            .message-container {
                box-shadow: 0 0 18px 8px rgba(0, 0, 0, 0.1), 0 0 32px 32px rgba(0, 0, 0, 0.08);
                width: 400px;
                right: -25px;
                bottom: 75px;
                max-height: 400px;
                position: absolute;
                transition: max-height .2s ease;
                font-family: Helvetica, Arial ,sans-serif;
                border-radius: 5px;

            }
            .message-container.hidden {
                max-height: 0px;
            }
            .message-container h2 {
                margin: 0;
                padding: 20px 20px;
                color: #fff;
                background-color: #e8701a;
                border-radius: 5px;
            }
            .message-container .content {
                margin: 20px 10px ;
                // border: 1px solid #e8701a;
                padding: 10px;
                display: flex;
                background-color: #fff;
                flex-direction: column;
            }
            .message-container form * {
                margin: 5px 0;
            }
            .message-container form input {
                padding: 10px;
            }
            .message-container form textarea {
                height: 100px;
                padding: 10px;
            }
            .message-container form textarea::placeholder {
                font-family: Helvetica, Arial ,sans-serif;
            }
            .message-container form button {
                cursor: pointer;
                background-color: #e8701a;
                color: #fff;
                border: 0;
                border-radius: 4px;
                padding: 10px;
            }
            .message-container form button:hover {
                background-color: #16632f;
            }
        `.replace(/^\s+|\n/gm, '');
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

    submit(event) {
        event.preventDefault();
        const formSubmission = {
            email: event.srcElement.querySelector('#email').value,
            message: event.srcElement.querySelector('#message').value,
        };

        this.messageContainer.innerHTML = '<h2>Thanks for your submission.</h2><p class="content">Someone will be in touch with your shortly regarding your enquiry';

        console.log(formSubmission);
    }

}


export {Widget}