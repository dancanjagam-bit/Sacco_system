import React from "react";
import "./App.css";
import MembersList from "./components/MembersList";
import LoansList from "./components/LoansList";
import LoanForm from "./components/LoanForm";
import LoanRepaymentForm from "./components/LoanRepaymentForm";

function App() {
  return (
    <div className="App">
      <h1>SACCO Dashboard</h1>

      {/* Members Section */}
      <section>
        <MembersList />
      </section>

      {/* Loans Section */}
      <section>
        <LoansList />
      </section>

      {/* Loan Application */}
      <section>
        <LoanForm />
      </section>

      {/* Loan Repayment */}
      <section>
        <LoanRepaymentForm />
      </section>
    </div>
  );
}

export default App;

