import {Box, Button} from '@mui/material';
import {useNavigate} from 'react-router';
import ScoreTable from '../ScoreTable';
import {UserRole} from '../../lib/backend';

export default function GameFinished({room}) {
    const navigate = useNavigate();

    return (
        <Box>
            <ScoreTable room={room} />
            
            {room.role === UserRole.ADMIN && (
                <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={() => navigate('/')}
                    >
                        Exit
                    </Button>
                </Box>
            )}
        </Box>
    );
} 