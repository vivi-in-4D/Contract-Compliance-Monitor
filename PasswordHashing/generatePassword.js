// Usage: "node generatePassword.js [password]"
// Outputs: Salt, Hashed Password

const bcrypt = require('bcrypt');

const saltRounds = 10;
const db_pepper = "23af"; // This has to be the same as the HASHPEPPER ENV variable in database

const alphanumerical = "0123456789abcdefghijklmnopqrstuvwxyz";

// Generate a random 4 alphanumerical salt value
let db_salt = "";
for (let i = 0; i < 4; i++) {
    let x = Math.floor(Math.random() * 36);
    db_salt += alphanumerical[x];
}
console.log("Salt: " + db_salt); // This is the salt value that has to be stored in database

// Method used to generate hash
let password = process.argv[2];
let combinedPass = db_salt + password + db_pepper;
//console.log("Combined Password: " + combinedPass);
bcrypt.genSalt(saltRounds, function(err, salt) {
    bcrypt.hash(combinedPass, salt, function (err, hash) {
        console.log("Hash is: " + hash);
    })
})