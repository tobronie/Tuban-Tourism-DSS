<?php
include '../config.php';

$id_matrix = $_GET['id_matrix'];
$result = mysqli_query($config, "SELECT id_alternatif FROM matrix_keputusan WHERE id_matrix='$id_matrix'");
$row = mysqli_fetch_assoc($result);
$id_alternatif = $row['id_alternatif'];
mysqli_query($config, "DELETE FROM matrix_keputusan WHERE id_alternatif='$id_alternatif'");
header("location: ../tampil/datamatrix.php");
?>