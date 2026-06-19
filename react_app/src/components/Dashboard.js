import React, { useEffect, useState } from "react";
import axios from "axios";

import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer
} from "recharts";

function Dashboard() {
  const [data, setData] = useState(null);
  const [phone, setPhone] = useState("");
  const [member, setMember] = useState(null);

  useEffect(() => {
    axios
      .get("/api/dashboard/")
      .then((res) => setData(res.data))
      .catch((err) => console.error(err));
  }, []);

  const searchMember = () => {
    if (!phone) return;

    axios
      .get(`/api/dashboard/member/${phone}/`)
      .then((res) => setMember(res.data))
      .catch((err) => console.error(err));
  };

  if (!data) return <p>Loading dashboard...</p>;

  // Chart data
  const pieData = [
    { name: "Savings", value: data.total_savings },
    { name: "Loans", value: data.total_loans },
    { name: "Repayments", value: data.total_repayments },
  ];

  const barData = [
    { name: "Members", value: data.total_members },
    { name: "Active Loans", value: data.active_loans },
  ];

  const COLORS = ["#4CAF50", "#FF9800", "#2196F3"];

  return (
    <div style={{ padding: "20px" }}>

      <h2>SACCO Dashboard</h2>

      {/* STATS */}
      <div style={{ display: "flex", gap: "20px" }}>
        <div>👥 Members: {data.total_members}</div>
        <div>💰 Savings: {data.total_savings}</div>
        <div>🏦 Loans: {data.total_loans}</div>
        <div>📊 Active Loans: {data.active_loans}</div>
      </div>

      {/* CHARTS SECTION */}
      <div style={{ display: "flex", marginTop: "30px" }}>

        {/* PIE CHART */}
        <div style={{ width: "50%", height: 300 }}>
          <h3>Financial Overview</h3>

          <ResponsiveContainer>
            <PieChart>
              <Pie
                data={pieData}
                dataKey="value"
                nameKey="name"
                outerRadius={100}
                label
              >
                {pieData.map((entry, index) => (
                  <Cell key={index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* BAR CHART */}
        <div style={{ width: "50%", height: 300 }}>
          <h3>System Stats</h3>

          <ResponsiveContainer>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#4CAF50" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* MEMBER SEARCH */}
      <hr />

      <h3>Search Member</h3>

      <input
        type="text"
        placeholder="Enter phone number"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
      />

      <button onClick={searchMember}>Search</button>

      {/* MEMBER RESULT */}
      {member && (
        <div style={{ marginTop: "20px" }}>
          <h4>{member.member}</h4>
          <p>📞 {member.phone}</p>
          <p>💰 Balance: {member.balance}</p>
          <p>🏦 Loan Balance: {member.loan_balance}</p>
          <p>💵 Savings: {member.total_savings}</p>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
