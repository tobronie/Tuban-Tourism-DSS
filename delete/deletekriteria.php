<?php
    include '../config.php';

    $id_kriteria = $_GET['id_kriteria'];

    mysqli_query($config,  "delete from kriteria WHERE id_kriteria='$id_kriteria'");

    header("location: ../tampil/datakriteria.php");
?>