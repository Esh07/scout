import React, { useEffect, useState } from "react";
import styles from "./HomePage.module.scss";
import { makeStyles } from "@material-ui/core/styles";
import Grid from "@material-ui/core/Grid";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import Typography from "@material-ui/core/Typography";
import ScilifelabLogo from "assets/SciLifeLab_Logotype_POS.png";
import ScilifelabLogoDark from "assets/SciLifeLab_Logotype_NEG.png";
import KarolinskaLogoDark from "assets/ki_logo_neg.png";
import KarolinskaLogo from "assets/ki_logo_pos.png";
import SwedacLogo from "assets/swedac.png";
import Divider from "@material-ui/core/Divider";

const useStyles = makeStyles({
  root: {
    minWidth: 275,
    width: "50vw",
    height: "30vh",
  },
  title: {
    fontSize: 35,
  },
  pos: {
    marginBottom: 30,
    marginTop: 20,
  },
  version: {
    marginTop: 30,
  },
});
const HomePage: React.FC = () => {
  const [darkMode, setDarkMode] = useState(false);
  // eslint-disable-next-line
  useEffect(() => {
    /** Check local storage */
    const darkModeStorage = localStorage.getItem("darkMode");
    if (darkModeStorage !== undefined) {
      setDarkMode(darkModeStorage === "true");
      return;
    }
  });
  const classes = useStyles();
  return (
    <div className={styles.container}>
      <Grid container justify="center" xs={12} className={styles.container}>
        <Grid item>
          <Card className={classes.root} variant="outlined">
            <CardContent>
              <Typography className={classes.title} gutterBottom variant="h1">
                Scout
              </Typography>
              <Typography>Analyze VCFs quicker and easier</Typography>
              <Divider className={classes.pos} />
              <Typography variant="body2" component="p">
                Scout allows you to browse VCFs in a web browser, identify
                compound pairs, and solve cases as a team.
              </Typography>
              <Typography
                className={classes.version}
                variant="body2"
                component="p"
              >
                Version x.xx
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      <div className={styles.logosContainer}>
        <Grid container spacing={8} justify="center" alignItems="center">
          <Grid item>
            <img
              className={styles.karolinskaLogo}
              src={`${darkMode ? KarolinskaLogoDark : KarolinskaLogo}`}
              alt="Karolinska Logo"
            />
          </Grid>
          <Grid item>
            <img
              className={styles.sciLifeLabLogo}
              src={`${darkMode ? ScilifelabLogoDark : ScilifelabLogo}`}
              alt="Scilifelab Logo"
            />
          </Grid>
          <Grid item>
            <img
              className={styles.swedacLogo}
              src={SwedacLogo}
              alt="Swedac Logo"
            />
          </Grid>
        </Grid>
      </div>
    </div>
  );
};
export default HomePage;
