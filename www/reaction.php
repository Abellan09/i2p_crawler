<html>
	<body>
		<?php
			$myPDO = new PDO('sqlite:i2p_database.db');
			if ($myPDO->connect_error) {
				die("Connection failed: " . $myPDO->connect_error);
			} 
			$node_id = $_POST["bola"];
			$result = $myPDO->query("SELECT id, name, outgoing_sites, incoming_sites, degree FROM Nodes WHERE id=$node_id");
			if ($result->num_rows >= 0) {
				foreach($result as $row)
				{
					echo "Name:" . "&nbsp;&nbsp;" . $row['name'] . "<br/>";
					echo "ID:" . "&nbsp;&nbsp;" . $row['id'] . "<br/>";
					echo "Outgoing Sites:" . "&nbsp;&nbsp;" . $row['outgoing_sites'] . "<br/>";
					echo "Incoming Sites:" . "&nbsp;&nbsp;" . $row['incoming_sites'] . "<br/>";
					echo "Degree:" . "&nbsp;&nbsp;" . $row['degree'];
				}
			}
			else {
				echo "The query does not return anything";
			}
		?>
	</body>
</html>