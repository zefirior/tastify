import * as React from 'react';
import CssBaseline from '@mui/material/CssBaseline';
import Divider from '@mui/material/Divider';
import AppTheme from '../components/theme/AppTheme';
import Features from './components/Features.jsx';
import Footer from '../components/Footer.jsx';
import HeaderBar from '../components/HeaderBar.jsx';

export default function MarketingPage(props) {
    return (
        <>
            <AppTheme {...props}>
                <CssBaseline enableColorScheme />
                <HeaderBar />
                <div>
                    <Features />
                    <Divider />
                    <Footer />
                </div>
            </AppTheme>
        </>
    );
}
