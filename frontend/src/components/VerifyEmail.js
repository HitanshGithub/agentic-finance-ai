import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { verifyEmail } from '../api';
import './Auth.css';

function VerifyEmail() {
    const { token } = useParams();
    const [loading, setLoading] = useState(true);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        const verify = async () => {
            try {
                await verifyEmail(token);
                setSuccess(true);
            } catch (err) {
                setError(err.response?.data?.detail || 'Verification failed. The link may be expired or invalid.');
            } finally {
                setLoading(false);
            }
        };

        if (token) {
            verify();
        } else {
            setError('Invalid verification link');
            setLoading(false);
        }
    }, [token]);

    if (loading) {
        return (
            <div className="auth-container">
                <div className="auth-card">
                    <div className="auth-header">
                        <h1>⏳ Verifying...</h1>
                        <p>Please wait while we verify your email</p>
                    </div>
                    <div style={{ textAlign: 'center', padding: '20px' }}>
                        <span className="spinner" style={{ width: '40px', height: '40px', borderWidth: '3px' }}></span>
                    </div>
                </div>
            </div>
        );
    }

    if (success) {
        return (
            <div className="auth-container">
                <div className="auth-card">
                    <div className="auth-header">
                        <h1>✅ Email Verified!</h1>
                    </div>

                    <div className="success-message">
                        <h3>You're all set!</h3>
                        <p>Your email has been verified successfully. You can now sign in to your account.</p>
                    </div>

                    <Link to="/login" className="auth-button" style={{ display: 'block', textAlign: 'center', marginTop: '30px', textDecoration: 'none' }}>
                        Sign In
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="auth-container">
            <div className="auth-card">
                <div className="auth-header">
                    <h1>❌ Verification Failed</h1>
                </div>

                <div className="error-message">
                    {error}
                </div>

                <div className="auth-footer" style={{ marginTop: '30px' }}>
                    <Link to="/signup">Try signing up again</Link>
                </div>
            </div>
        </div>
    );
}

export default VerifyEmail;
