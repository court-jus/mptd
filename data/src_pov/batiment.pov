
#declare t_mur = texture
	{
	pigment {
		color rgb x
		}
	}

#declare t_vitres = texture
	{
	pigment
		{
		image_map
			{
			png
			"texture_vitres.png"
			}
			scale 0.5
		}
	}

#declare t_brouz = texture
	{
	pigment {
		color rgb x + y
		}
	}

#declare brouzouf = height_field
	{
	png
	"brouzouf.png"
	texture { t_brouz }
	rotate x*90
	scale z*0.3
	}
#declare batiment = union
	{
	box
		{
		<-1,0,-1>,
		<1,2.3,1>
		texture { t_vitres }
		}
	object
		{
		brouzouf
		translate <-0.5,2,-1.1>
		}
	box
		{
		<-0.5,0.6,-1.3>,
		<0.5,0.65,-1>
		texture { t_mur }
		}
	cylinder
		{
		< 0.4,0,-1.15>,
		< 0.4,0.65,-1.15>,
		0.08
		texture { t_mur }
		}
	cylinder
		{
		<-0.4,0,-1.15>,
		<-0.4,0.65,-1.15>,
		0.08
		texture { t_mur }
		}
	}

camera
	{
	location <-1.5,2,-3>
	look_at  <1,1,0>
	right 1.39 * x
	}

light_source
	{
	<-3,7,-5>
	color rgb 1
	}

background
	{
	color rgb 0.6
	}

object { batiment }
