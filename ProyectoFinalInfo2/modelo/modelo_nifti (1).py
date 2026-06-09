import numpy as np
import nibabel as nib
class ModeloNifti:
    def __init__(self):
        self.volume = None
        self.spacing = (1.0, 1.0, 1.0)
        self.affine = np.eye(4)
    def guardar_dicom_a_nifti(self, volume_hu, spacing, first_position, output_filepath):

        try:
            dz, dy, dx = spacing

            volume_nii = np.transpose(volume_hu, (2, 1, 0))

            affine = np.eye(4)
            affine[0, 0] = dx
            affine[1, 1] = dy
            affine[2, 2] = dz
            
            if first_position is not None and len(first_position) == 3:
                affine[0, 3] = first_position[0]
                affine[1, 3] = first_position[1]
                affine[2, 3] = first_position[2]
            
            nii_img = nib.Nifti1Image(volume_nii, affine)
            
            nib.save(nii_img, output_filepath)
            print(f"Volumen guardado exitosamente en NIfTI: {output_filepath}")
            return True
        except Exception as e:
            print(f"Error al convertir DICOM a NIfTI: {e}")
            raise IOError(f"No se pudo guardar el archivo NIfTI: {e}")
    def cargar_nifti(self, filepath):

        try:
            nii_img = nib.load(filepath)
            data = nii_img.get_fdata() 
            zooms = nii_img.header.get_zooms()
            dx, dy, dz = zooms[0], zooms[1], zooms[2]
            
            self.affine = nii_img.affine
            
            self.volume = np.transpose(data, (2, 1, 0))
            self.spacing = (dz, dy, dx)
            
            return self.volume, self.spacing
        except Exception as e:
            print(f"Error al cargar archivo NIfTI: {e}")
            raise IOError(f"El archivo NIfTI está corrupto o es inválido: {e}")
