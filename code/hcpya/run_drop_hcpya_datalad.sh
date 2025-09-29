#!/usr/bin/expect

# Set timeout for responses
set timeout -1

# Spawn the shell script that includes datalad get
spawn drop_hcpya_datalad.sh

expect {
    "key_id:" {
        send "AKIAXO65CT57CXVQ46NU\r"
        exp_continue
    }
    "secret_id:" {
        send "vTMK9qNOt01wJwH2FaLkB9wV7aU3dhWCK8qY9MpF\r"
        exp_continue
    }
    eof {
        # End of file (script finished)
        puts "Script execution completed."
    }
}