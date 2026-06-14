import React, { useEffect, useState } from "react";
import axios from "axios";

function MembersList() {
  const [members, setMembers] = useState([]);

  useEffect(() => {
    axios.get("/api/members/")
      .then(response => setMembers(response.data))
      .catch(error => console.error(error));
  }, []);

  return (
    <div>
      <h2>Members</h2>
      <table>
        <thead>
          <tr>
            <th>Name</th><th>Phone</th><th>Email</th><th>Balance</th>
          </tr>
        </thead>
        <tbody>
          {members.map(member => (
            <tr key={member.id}>
              <td>{member.name}</td>
              <td>{member.phone}</td>
              <td>{member.email}</td>
              <td>{member.balance}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default MembersList;
