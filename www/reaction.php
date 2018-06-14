<html>
	<body>
		<?php
			$myPDO = new PDO('sqlite:i2p_database.db');
			if ($myPDO->connect_error) {
				die("Connection failed: " . $myPDO->connect_error);
				echo "CONEXIÓN FALLIDA";
			} 
			$node_id = $_POST["bola"];
			$result = $myPDO->query("SELECT id, name, degree FROM Nodes WHERE id=$node_id");
			if ($result->num_rows >= 0) {
				foreach($result as $row)
				{
					echo "id:" . "&nbsp;&nbsp;" . $row['id'] . "<br/>";
					echo "name:" . "&nbsp;&nbsp;" . $row['name'] . "<br/>";
					echo "degree:" . "&nbsp;&nbsp;" . $row['degree'];
				}
			}
			else {
				echo "Consulta no devuelve nada.";
			}
		?>
	</body>
</html>