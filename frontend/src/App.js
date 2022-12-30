import logo from './logo.svg';
import './App.css';

function App() {
  const nodeMode = process.env.NODE_ENV;
  const isDevelopment = process.env.NODE_ENV === 'development';
  const fastapiUrl = process.env.REACT_APP_DEV_FASTAPI_URL;

  const getUrl = (uri) => {
    if (isDevelopment) {
      return `${fastapiUrl}${uri}`;
    } else {
      return uri;
    }
  }

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>Edit <code>src/App.js</code> and save to reload.</p>
        <div>Mode : <b>{nodeMode}</b></div>
        <div>Is development : <b>{isDevelopment ? 'true' : 'false'}</b></div>
        {isDevelopment && <div>FastApi Url : <a href={fastapiUrl}>{fastapiUrl}</a></div>}
        <a className="App-link" href={getUrl("/docs")} rel="noopener noreferrer">Fastapi documentation</a>
      </header>
    </div>
  );
}

export default App;
