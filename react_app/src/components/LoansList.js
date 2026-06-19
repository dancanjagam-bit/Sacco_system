import React, { useEffect, useState } from "react";
import axios from "axios";
import LoanRepaymentForm from "./LoanRepaymentForm";
import RepaymentHistory from "./RepaymentHistory";

function LoansList() {
  const [loans, setLoans] = useState([]);
  const [showActiveOnly, setShowActiveOnly] = useState(false);

  const role = localStorage.getItem("role");
  const token = localStorage.getItem("token");

  const fetchLoans = () => {
    axios.get("/api/loans/", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then(response => setLoans(response.data))
      .catch(error => console.error(error));
  };

  useEffect(() => {
    fetchLoans();
  }, []);

  const approveLoan = async (id) => {
    try {
      await axios.post(
        `/api/loans/${id}/approve/`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      fetchLoans();
    } catch (error) {
      console.error(error);
      alert("Failed to approve loan");
    }
  };

  const rejectLoan = async (id) => {
    try {
      await axios.post(
        `/api/loans/${id}/reject/`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      fetchLoans();
    } catch (error) {
      console.error(error);
      alert("Failed to reject loan");
    }
  };

  const filteredLoans = showActiveOnly
    ? loans.filter(
        loan =>
          loan.balance !== "0.00" &&
          loan.status !== "REPAID" &&
          loan.status !== "rejected"
      )
    : loans;

  const getRowClass = (loan) => {
    const status = String(loan.status).toLowerCase();

    if (loan.balance === "0.00" || status === "repaid") {
      return "repaid-row";
    }

    if (status === "pending") {
      return "pending-row";
    }

    if (status === "approved") {
      return "approved-row";
    }

    if (status === "rejected") {
      return "rejected-row";
    }

    return "";
  };

  return (
    <div>
      <h2>Loans</h2>

      <button onClick={() => setShowActiveOnly(!showActiveOnly)}>
        {showActiveOnly
          ? "Show All Loans"
          : "Show Only Active Loans"}
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
          {filteredLoans.map((loan) => (
            <tr key={loan.id} className={getRowClass(loan)}>
              <td>{loan.member}</td>
              <td>{loan.amount}</td>

              <td>
                {loan.balance === "0.00"
                  ? "REPAID"
                  : loan.status}
              </td>

              <td>{loan.balance}</td>

              <td>

                {/* ADMIN ONLY */}
                {role === "admin" &&
                  String(loan.status).toLowerCase() === "pending" && (
                    <>
                      <button
                        onClick={() => approveLoan(loan.id)}
                      >
                        Approve
                      </button>

                      <button
                        onClick={() => rejectLoan(loan.id)}
                      >
                        Reject
                      </button>
                    </>
                  )}

                <LoanRepaymentForm
                  loanId={loan.id}
                  onRepayment={fetchLoans}
                />

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
