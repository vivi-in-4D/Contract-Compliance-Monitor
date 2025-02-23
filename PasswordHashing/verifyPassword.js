// Usage: "node verifyPassword [password] [salt]"
// Output: Comparion of password to passhash
// Note: Usually you would get the salt from the database and not the commandline. This is just for testing purposes.

const bcrypt = require('bcrypt');

const db_pepper = "23af"; // This has to be same as pepper used to generate password
const passHash = "$2b$10$453zuxs5Dlon6hpng/3aAuoBAEbfvHAD8bw9QYQiJ0LnSROSNv32O";
const args = process.argv;

let password = args[2];
let salt = args[3];

// Check Password
let combinedPass = salt + password + db_pepper;
bcrypt.compare(combinedPass, passHash, (_, result) => {
    console.log("Comparison: " + result);
})