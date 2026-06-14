import React, { useEffect, useState } from "react";
import axios from "axios";
import LoanRepaymentForm from "./LoanRepaymentForm";
import RepaymentHistory from "./RepaymentHistory";

function LoansList() {
  const [loans, setLoans] = useState([]);
  const [showActiveOnly, setShowActiveOnly] = useState(false);

  const fetchLoans = () => {
    axios.get("/api/loans/")
      .then(response => setLoans(response.data))
      .catch(error => console.error(error));
  };

  useEffect(() => {
    fetchLoans();
  }, []);

  const approveLoan = (id) => {
    axios.patch(`/api/loans/${id}/`, { status: "APPROVED" })
      .then(() => {
        setLoans(loans.map(loan =>
          loan.id === id ? { ...loan, status: "APPROVED" } : loan
        ));
      })
      .catch(error => console.error(error));
  };

  const filteredLoans = showActiveOnly
    ? loans.filter(loan => loan.balance !== "0.00" && loan.status !== "REPAID")
    : loans;

  return (
    <div>
      <h2>Loans</h2>
      <button onClick={() => setShowActiveOnly(!showActiveOnly)}>
        {showActiveOnly ? "Show All Loans" : "Show Only Active Loans"}
      </button>
      <table>
        <thead>
          <tr>
            <th>Member</th>
            <th>Amount</th>
            <th>Status</th>
            <th>Balance</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {filteredLoans.map(loan => (
            <tr
              key={loan.id}
              className={loan.balance === "0.00" || loan.status === "REPAID" ? "repaid-loan" : ""}
            >
              <td>{loan.member}</td>
              <td>{loan.amount}</td>
              <td>{loan.balance === "0.00" ? "REPAID" : loan.status}</td>
              <td>{loan.balance}</td>
              <td>
                {loan.status === "PENDING" && (
                  <button onClick={() => approveLoan(loan.id)}>Approve</button>
                )}
                <LoanRepaymentForm loanId={loan.id} onRepayment={fetchLoans} />
                <RepaymentHistory loanId={loan.id} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default LoansList;

