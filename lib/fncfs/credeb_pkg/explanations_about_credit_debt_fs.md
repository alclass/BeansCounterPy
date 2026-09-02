  input: credit_account, debt_account
  output: new_credit_account, new_debt_account

  Example:
    ex1:
      input:
        cre_account = 100
        deb_account = -200
      output:
        new_cre_account = 0
        new_deb_account = -100
    ex2:
      input:
        cre_account = 200
        deb_account = -100
      output:
        new_cre_account = 100
        new_deb_account = 0
    ex3:
      input:
        cre_account = 100
        deb_account = -100
      output:
        new_cre_account = 0
        new_deb_account = 0
