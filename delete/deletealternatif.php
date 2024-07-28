<?php
    include '../config.php';

    $id_alternatif = $_GET['id_alternatif'];

    mysqli_query($config,  "delete from alternatif WHERE id_alternatif='$id_alternatif'");

    header("location: ../tampil/dataalternatif.php");
?>