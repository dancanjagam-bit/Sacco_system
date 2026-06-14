import React, { useEffect, useState } from "react";
import axios from "axios";

function RepaymentHistory({ memberId }) {
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    axios.get("/api/transactions/")
      .then(response => {
        // filter only repayments for this member
        const repayments = response.data.filter(
          tx => tx.member === memberId && tx.source === "Loan Repayment"
        );
        setTransactions(repayments);
      })
      .catch(error => console.error(error));
  }, [memberId]);

  return (
    <div>
      <h4>Repayment History</h4>
      {transactions.length === 0 ? (
        <p>No repayments yet.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Amount</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map(tx => (
              <tr key={tx.id}>
                <td>{tx.amount}</td>
                <td>{new Date(tx.date).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default RepaymentHistory;
