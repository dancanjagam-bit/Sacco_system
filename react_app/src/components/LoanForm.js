import React, { useState } from "react";
import axios from "axios";

function LoanForm() {
  const [memberId, setMemberId] = useState("");
  const [amount, setAmount] = useState("");

  const applyLoan = () => {
    axios.post("/api/loans/", {
      member: memberId,   // must be the member's ID
      amount: amount,
      balance: amount     // initialize balance equal to amount
    })
      .then(() => alert("Loan application submitted"))
      .catch(error => alert("Error: " + error));
  };

  return (
    <div>
      <h2>Apply for Loan</h2>
      <input
        type="text"
        placeholder="Member ID"
        value={memberId}
        onChange={e => setMemberId(e.target.value)}
      />
      <input
        type="number"
        placeholder="Amount"
        value={amount}
        onChange={e => setAmount(e.target.value)}
      />
      <button onClick={applyLoan}>Apply</button>
    </div>
  );
}

export default LoanForm;

