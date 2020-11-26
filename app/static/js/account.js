// Copyright 2016, Google, Inc.
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

$(function(){
    // This is the host for the backend.
    // TODO: When running Firenotes locally, set to http://localhost:8081. Before
    // deploying the application to a live production environment, change to
    // https://backend-dot-<PROJECT_ID>.appspot.com as specified in the
    // backend's app.yaml file.
    var backendHostUrl = 'http://localhost:5000';
  
    // [START gae_python_firenotes_config]
    // Obtain the following from the "Add Firebase to your web app" dialogue
    // Initialize Firebase
    var config = {
        apiKey: "AIzaSyAcxxRO8Sqf7m8F9NkUI6-9MPdWrZkYgGs",
        authDomain: "savemygpa-7912d.firebaseapp.com",
        databaseURL: "https://savemygpa-7912d.firebaseio.com",
        projectId: "savemygpa-7912d",
        storageBucket: "savemygpa-7912d.appspot.com",
        messagingSenderId: "781502539376",
        appId: "1:781502539376:web:7618817f841ef51f9b36b5"
    };
});

function signUpWithEmailPassword() {
  var email_reg = document.getElementById('email_reg');
  var password_reg = document.getElementById('password_reg');
  // [START auth_signup_password]
  firebase.auth().createUserWithEmailAndPassword(email_reg, password_reg)
    .then((user) => {
      // Signed in 
      // ...
    })
    .catch((error) => {
      var errorCode = error.code;
      var errorMessage = error.message;
      // ..
    });
  // [END auth_signup_password]
  // This is a template from the tutorial online
  // You can use javascript or just send the input to the backend to authenticate
  // https://github.com/thisbejim/Pyrebase
}

window.onload=function() {
  var regButton = document.getElementById('register');
  regButton.addEventListener('click', handler_reg);
  // You can make something similar like this for the login if you are going to use javascript for authentication
}

function handler_reg() {
  // Send the input value to the firebase to authenticate
  // Alert if successful, send error if not
  // @app.route('/register', methods=['GET']) should be changed accordingly 
  // (go back to main page if successful, stay on the account page if not)
}