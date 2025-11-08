import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { loadStripe } from '@stripe/stripe-js';

const stripePromise = loadStripe('your_stripe_publishable_key');

function App() {
  const [courses, setCourses] = useState([]);
  const [user, setUser] = useState(null);
  const [form, setForm] = useState({ email: '', password: '', name: '' });

  useEffect(() => {
    axios.get('http://localhost:5000/api/courses')
      .then(res => setCourses(res.data))
      .catch(console.error);
  }, []);

  const login = () => {
    axios.post('http://localhost:5000/api/login', { email: form.email, password: form.password }, { withCredentials: true })
      .then(() => setUser(form.email))
      .catch(() => alert('Login failed'));
  };

  const register = () => {
    axios.post('http://localhost:5000/api/register', { email: form.email, password: form.password, name: form.name })
      .then(() => alert('Registered!'))
      .catch(() => alert('Registration failed'));
  };

  const buyCourse = async (course_id) => {
    if (!user) return alert("Please log in first.");
    try {
      const res = await axios.post('http://localhost:5000/create-checkout-session', { course_id }, { withCredentials: true });
      const stripe = await stripePromise;
      await stripe.redirectToCheckout({ sessionId: res.data.id });
    } catch (e) {
      alert("Payment failed");
    }
  };

  return (
    <div>
      <h1>Courses</h1>
      {!user && (
        <div>
          <input placeholder="Name" onChange={e => setForm({ ...form, name: e.target.value })} />
          <input placeholder="Email" onChange={e => setForm({ ...form, email: e.target.value })} />
          <input type="password" placeholder="Password" onChange={e => setForm({ ...form, password: e.target.value })} />
          <button onClick={register}>Register</button>
          <button onClick={login}>Login</button>
        </div>
      )}
      {user && <h2>Welcome, {user}</h2>}
      <ul>
        {courses.map(c => (
          <li key={c.id}>{c.title} - ${(c.price / 100).toFixed(2)} <button onClick={() => buyCourse(c.id)}>Buy</button></li>
        ))}
      </ul>
    </div>
  );
}

export default App;
