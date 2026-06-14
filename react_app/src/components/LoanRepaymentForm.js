import React, { useState } from "react";
import axios from "axios";

function LoanRepaymentForm({ loanId, onRepayment }) {
  const [amount, setAmount] = useState("");
  const [message, setMessage] = useState("");

  const repayLoan = () => {
    axios.post(`/api/loans/${loanId}/repay/`, { amount })
      .then(response => {
        setMessage(`Repayment successful. Remaining Balance: ${response.data.balance}`);
        if (onRepayment) onRepayment(); // refresh loan list
      })
      .catch(error => {
        setMessage("Error: " + (error.response?.data?.error || "Unexpected error"));
      });
  };

  return (
    <div>
      <input
        type="number"
        placeholder="Amount"
        value={amount}
        onChange={e => setAmount(e.target.value)}
      />
      <button onClick={repayLoan}>Repay</button>
      {message && <p>{message}</p>}
    </div>
  );
}

export default LoanRepaymentForm;

