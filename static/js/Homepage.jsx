import React from "react";
import { Link } from "react-router-dom";
import { Carousel } from "react-bootstrap";
import "./Homepage.css";
import logo from "./img/RideFlow.png";
import slidePage1 from "./img/slide_page_1.jpg";
import slidePage2 from "./img/slide_page_2.jpg";
import slidePage3 from "./img/slide_page_3.jpg";
import MainFooter from './../../Components/MainFooter';

const Homepage = () => {
  return (
    <div>
      <header id="header" className="header fixed shadow">
        <div className="header__container">
          <div className="header-logo-container">
            <Link to="/">
              <img id="logo" className="header__logo" src={logo} alt="RideFlow" />
            </Link>
          </div>
          <ul className="header__menu">
            <li className="header__menu-item">
              <Link to="/login" className="hover-target">Log in</Link>
            </li>
            <li className="header__menu-item">
              <Link to="/register" className="hover-target">Register</Link>
            </li>
          </ul>
        </div>
      </header>

      <main style={{ clear: "both", marginTop: "-90px", background: "white" }}>
        <Carousel>
          <Carousel.Item>
              <img className="d-block w-100" src={slidePage1} alt="First slide" />
          </Carousel.Item>
          <Carousel.Item>
              <img className="d-block w-100" src={slidePage2} alt="Second slide" />
          </Carousel.Item>
          <Carousel.Item>
              <img className="d-block w-100" src={slidePage3} alt="Third slide" />
          </Carousel.Item>
        </Carousel>
      </main>

      <MainFooter />
    </div>
  );
};

export default Homepage;
