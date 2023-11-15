// styles.js

const styles = `
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
                bottom: 95px;
                max-height: 600px;
                position: absolute;
                transition: max-height .2s ease;
                font-family: Helvetica, Arial ,sans-serif;
                border-radius: 5px;
                background: #e2e2e2e2;
                font-size: 13px;

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
                padding: 10px;
                display: flex;
                background-color: #fff;
                flex-direction: column;
            }
            .message-container form * {
                margin: 5px 10px 0px 0;
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
            button {
                cursor: pointer;
                background-color: #e8701a;
                color: #fff;
                border: 0;
                border-radius: 4px;
                padding: 10px;
            }
            .message-container form button:hover {
                background-color: #43e66e;
            }
            
            .available-time-a {
              display: inline-block;
              background-color: #fff;
              border-radius: 24px;
              border-style: none;
              box-shadow: rgba(0, 0, 0, .2) 0 3px 5px -1px,rgba(0, 0, 0, .14) 0 6px 10px 0,rgba(0, 0, 0, .12) 0 1px 18px 0;
              box-sizing: border-box;
              color: #3c4043;
              font-size: 14px;
              font-weight: 500;
              height: 48px;
              width: 80px;
              margin: 2%;
              padding: 0;
              text-align: center;
              padding-top: 16px;
            }
            
            .available-time-a:hover {
                // border: 6px solid #43e66e;
                text-decoration: none;
                background: #43e66e;
            }
            
            .available-time-a:focus {
                // border: 6px solid #43e66e;
                text-decoration: none;
                background: red;
            }
            
            .selected {
                background: #43e66e;
            }
            
            input {
                color: black;
                border: 1px solid #555555;
                border-radius: 5px;
            }
            
            .time-buttons-content {
                margin: 20px 10px ;
                padding: 10px;
                background-color: #fff;
            }
            
            .submit-time-button {
                width: 100%;
            }
            
            .reservation-confirmed-text {
                font-size: 1.5em;
                margin-left: 5%;
            }
            
        `.replace(/^\s+|\n/gm, ''); // Remove leading spaces and line breaks

export default styles;
