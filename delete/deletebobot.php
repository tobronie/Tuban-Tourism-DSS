<?php
    include '../config.php';

    $id_bobot = $_GET['id_bobot'];

    mysqli_query($config,  "delete from bobot WHERE id_bobot='$id_bobot'");

    header("location: ../tampil/databobot.php");
?>